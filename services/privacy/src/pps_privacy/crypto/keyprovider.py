"""Data-key supply, with the KMS dependency behind an interface.

Every record is encrypted under its own data key (DEK); the DEK is stored next
to the record in wrapped form and can only be unwrapped by a key-encryption key
(KEK) the application never sees in plaintext. Destroying a user's DEK makes
every copy of their data unreadable, including ones in backups and object
versions -- this is how erasure actually reaches storage we cannot enumerate.

Two implementations:

- :class:`KmsKeyProvider` -- production. AWS KMS holds the KEK; it never leaves.
- :class:`LocalKeyProvider` -- development and tests. Refuses to start when the
  environment says production, so a misconfigured deploy fails loudly instead of
  quietly protecting data with a key sitting in an environment variable.

The team's "already established encryption mechanism" is still unconfirmed
(see docs/privacy/infra-residency-and-latency.md section 5). If it differs from
KMS envelope encryption, a third implementation of :class:`KeyProvider` is the
only thing that changes.

Deliberately absent: a plaintext-DEK cache. It would cut KMS latency, but it
also parks key material in process memory, and that tradeoff belongs to whoever
owns latency -- not to this module's defaults. Add it as a decorator around a
provider when the call is made, not inside one.
"""

from __future__ import annotations

import base64
import binascii
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .envelope import DEK_BYTES, CryptoError, decrypt, encrypt, wrap_aad

__all__ = [
    "KeyClass",
    "DataKey",
    "KeyProvider",
    "LocalKeyProvider",
    "KmsKeyProvider",
    "KeyProviderError",
]


class KeyProviderError(CryptoError):
    """Raised when a data key cannot be generated or unwrapped."""


class KeyClass(str, Enum):
    """One KEK per class of data, so a compromise is contained to that class.

    Separate CMKs also mean separate key policies and separate CloudTrail
    trails: "who decrypted resume files this week" is answerable without
    untangling it from session-token traffic.
    """

    IDENTITY = "identity"          # names, emails, phones
    RESUME_FILES = "resume_files"  # uploaded documents in S3
    LOGS = "logs"
    BACKUPS = "backups"


@dataclass(frozen=True)
class DataKey:
    """A freshly generated data key in both forms.

    ``plaintext`` is used immediately and then dropped; ``wrapped`` is what gets
    stored alongside the record. Never persist ``plaintext``, never log either.
    """

    plaintext: bytes
    wrapped: bytes

    def __repr__(self) -> str:  # pragma: no cover - defensive
        # Keeps key material out of tracebacks, logs and debugger output.
        return (
            f"DataKey(plaintext=<{len(self.plaintext)} bytes redacted>, "
            f"wrapped=<{len(self.wrapped)} bytes>)"
        )


class KeyProvider(ABC):
    """Generates and unwraps data keys for a given key class."""

    @abstractmethod
    def generate_data_key(self, key_class: KeyClass) -> DataKey:
        """Return a new random data key, plaintext plus wrapped form."""

    @abstractmethod
    def unwrap_data_key(self, wrapped: bytes, key_class: KeyClass) -> bytes:
        """Recover a plaintext data key. Raises :class:`KeyProviderError`."""


class LocalKeyProvider(KeyProvider):
    """Development and test provider. Never valid in production.

    Derives a per-class KEK from one master key with HKDF, so a single
    ``PPS_MASTER_KEY`` covers every class without reusing the same bytes for
    each -- the same separation KMS gives us with separate CMKs.
    """

    _ENV_VAR = "PPS_MASTER_KEY"

    def __init__(
        self,
        master_key: bytes | None = None,
        *,
        allow_in_production: bool = False,
    ) -> None:
        env = os.environ.get("PPS_ENV", "development").lower()
        if env in {"production", "prod"} and not allow_in_production:
            raise KeyProviderError(
                "LocalKeyProvider must not be used in production; configure "
                "KmsKeyProvider. This guard exists so a missing KMS config fails "
                "loudly rather than silently protecting student data with an "
                "environment variable."
            )

        if master_key is None:
            raw = os.environ.get(self._ENV_VAR)
            if not raw:
                raise KeyProviderError(
                    f"{self._ENV_VAR} is not set. Generate one with: "
                    "python -c "
                    '"import os,base64; print(base64.b64encode(os.urandom(32)).decode())"'
                )
            master_key = self._decode(raw)

        if len(master_key) < DEK_BYTES:
            raise KeyProviderError(f"master key must be at least {DEK_BYTES} bytes")
        self._master = master_key

    @staticmethod
    def _decode(raw: str) -> bytes:
        try:
            return base64.b64decode(raw, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise KeyProviderError(
                f"{LocalKeyProvider._ENV_VAR} must be base64-encoded"
            ) from exc

    def _kek(self, key_class: KeyClass) -> bytes:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=DEK_BYTES,
            salt=None,
            info=f"pps-kek:{key_class.value}".encode(),
        ).derive(self._master)

    def generate_data_key(self, key_class: KeyClass) -> DataKey:
        dek = os.urandom(DEK_BYTES)
        wrapped = encrypt(dek, self._kek(key_class), wrap_aad(key_class.value))
        return DataKey(plaintext=dek, wrapped=wrapped)

    def unwrap_data_key(self, wrapped: bytes, key_class: KeyClass) -> bytes:
        try:
            return decrypt(wrapped, self._kek(key_class), wrap_aad(key_class.value))
        except CryptoError as exc:
            raise KeyProviderError("could not unwrap data key") from exc


class KmsKeyProvider(KeyProvider):
    """Production provider backed by AWS KMS envelope encryption.

    ``key_arns`` maps each class to its own CMK. The KMS *encryption context* is
    set to the key class: KMS treats it as AAD, so a blob wrapped for one class
    cannot be decrypted as another, and the context is recorded in CloudTrail --
    which is what makes "who decrypted identity keys" auditable.

    Keep the CMKs single-region. A multi-region replica places copies of the key
    material in another jurisdiction, which quietly undoes the residency story
    (see docs/privacy/infra-residency-and-latency.md section 3).
    """

    def __init__(
        self,
        key_arns: dict[KeyClass, str],
        *,
        client: Any | None = None,
        region: str | None = None,
    ) -> None:
        missing = [c for c in KeyClass if c not in key_arns]
        if missing:
            names = ", ".join(c.value for c in missing)
            raise KeyProviderError(f"no CMK configured for: {names}")
        self._key_arns = key_arns
        self._client = client or self._default_client(region)

    @staticmethod
    def _default_client(region: str | None) -> Any:
        try:
            import boto3  # imported lazily so dev and tests need no AWS SDK
        except ImportError as exc:  # pragma: no cover - depends on install extras
            raise KeyProviderError(
                "boto3 is required for KmsKeyProvider; install the 'aws' extra"
            ) from exc
        return boto3.client("kms", region_name=region or os.environ.get("AWS_REGION"))

    @staticmethod
    def _context(key_class: KeyClass) -> dict[str, str]:
        return {"key_class": key_class.value}

    def generate_data_key(self, key_class: KeyClass) -> DataKey:
        try:
            resp = self._client.generate_data_key(
                KeyId=self._key_arns[key_class],
                KeySpec="AES_256",
                EncryptionContext=self._context(key_class),
            )
        except Exception as exc:  # noqa: BLE001 - botocore raises client-specific types
            raise KeyProviderError(
                f"KMS GenerateDataKey failed for {key_class.value}"
            ) from exc
        return DataKey(plaintext=resp["Plaintext"], wrapped=resp["CiphertextBlob"])

    def unwrap_data_key(self, wrapped: bytes, key_class: KeyClass) -> bytes:
        try:
            resp = self._client.decrypt(
                CiphertextBlob=wrapped,
                KeyId=self._key_arns[key_class],
                EncryptionContext=self._context(key_class),
            )
        except Exception as exc:  # noqa: BLE001
            raise KeyProviderError(f"KMS Decrypt failed for {key_class.value}") from exc
        return resp["Plaintext"]
