"""Tests for data-key supply and the crypto-shredding erasure model."""

from __future__ import annotations

import base64
import os
from typing import Any

import pytest

from pps_privacy.crypto import (
    DEK_BYTES,
    DecryptionError,
    KeyClass,
    KeyProviderError,
    KmsKeyProvider,
    LocalKeyProvider,
    decrypt,
    encrypt,
    field_aad,
)

MASTER = os.urandom(32)
AAD = field_aad("users", "name_enc", "user-1")


@pytest.fixture
def provider() -> LocalKeyProvider:
    return LocalKeyProvider(MASTER)


def test_generate_and_unwrap_round_trip(provider: LocalKeyProvider) -> None:
    key = provider.generate_data_key(KeyClass.IDENTITY)
    assert len(key.plaintext) == DEK_BYTES
    assert provider.unwrap_data_key(key.wrapped, KeyClass.IDENTITY) == key.plaintext


def test_each_data_key_is_unique(provider: LocalKeyProvider) -> None:
    """Per-record keys. Reusing one key would defeat per-user shredding."""
    keys = {provider.generate_data_key(KeyClass.IDENTITY).plaintext for _ in range(50)}
    assert len(keys) == 50


def test_wrapped_key_is_bound_to_its_class(provider: LocalKeyProvider) -> None:
    """A key wrapped for identity data must not unwrap as a resume-file key.

    This is what keeps a compromise of one data class from spreading.
    """
    key = provider.generate_data_key(KeyClass.IDENTITY)
    with pytest.raises(KeyProviderError):
        provider.unwrap_data_key(key.wrapped, KeyClass.RESUME_FILES)


def test_classes_derive_different_keks(provider: LocalKeyProvider) -> None:
    identity = provider.generate_data_key(KeyClass.IDENTITY)
    files = provider.generate_data_key(KeyClass.RESUME_FILES)
    # Different wrapping keys, so neither blob is usable under the other class.
    with pytest.raises(KeyProviderError):
        provider.unwrap_data_key(files.wrapped, KeyClass.IDENTITY)
    with pytest.raises(KeyProviderError):
        provider.unwrap_data_key(identity.wrapped, KeyClass.RESUME_FILES)


def test_crypto_shredding_makes_data_unrecoverable(provider: LocalKeyProvider) -> None:
    """The erasure model, end to end.

    We delete a student by destroying their wrapped DEK. The ciphertext may
    still exist in an S3 version or an RDS snapshot we cannot reach -- and it
    stays unreadable anyway, because nothing can reproduce the key.
    """
    key = provider.generate_data_key(KeyClass.IDENTITY)
    ciphertext = encrypt(b"Priya Sharma", key.plaintext, AAD)

    # Erasure: the wrapped DEK is deleted. Simulate a leftover copy of the data.
    del key

    # Any other key, including a fresh one from the same provider, is useless.
    replacement = provider.generate_data_key(KeyClass.IDENTITY)
    with pytest.raises(DecryptionError):
        decrypt(ciphertext, replacement.plaintext, AAD)


def test_tampered_wrapped_key_is_rejected(provider: LocalKeyProvider) -> None:
    key = provider.generate_data_key(KeyClass.IDENTITY)
    corrupted = bytearray(key.wrapped)
    corrupted[-1] ^= 0x01
    with pytest.raises(KeyProviderError):
        provider.unwrap_data_key(bytes(corrupted), KeyClass.IDENTITY)


def test_repr_does_not_leak_key_material(provider: LocalKeyProvider) -> None:
    """Key bytes must not reach a traceback, a log line or a debugger frame."""
    key = provider.generate_data_key(KeyClass.IDENTITY)
    rendered = repr(key)
    assert "redacted" in rendered
    assert key.plaintext.hex() not in rendered
    assert str(key.plaintext) not in rendered


# --- environment guards -------------------------------------------------


def test_refuses_to_run_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing KMS config must fail loudly, not fall back to a local key."""
    monkeypatch.setenv("PPS_ENV", "production")
    with pytest.raises(KeyProviderError, match="production"):
        LocalKeyProvider(MASTER)


def test_production_guard_can_be_overridden_explicitly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Deliberate, greppable escape hatch for break-glass tooling.
    monkeypatch.setenv("PPS_ENV", "production")
    assert LocalKeyProvider(MASTER, allow_in_production=True) is not None


def test_missing_master_key_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PPS_MASTER_KEY", raising=False)
    with pytest.raises(KeyProviderError, match="PPS_MASTER_KEY"):
        LocalKeyProvider()


def test_master_key_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPS_MASTER_KEY", base64.b64encode(MASTER).decode())
    assert LocalKeyProvider().generate_data_key(KeyClass.IDENTITY).plaintext


def test_malformed_master_key_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PPS_MASTER_KEY", "not base64!!")
    with pytest.raises(KeyProviderError, match="base64"):
        LocalKeyProvider()


def test_short_master_key_is_rejected() -> None:
    with pytest.raises(KeyProviderError, match="at least"):
        LocalKeyProvider(os.urandom(16))


# --- KMS provider, against a stub client --------------------------------


class _StubKms:
    """Records what would be sent to KMS so we can assert on the call shape."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def generate_data_key(self, **kwargs: Any) -> dict[str, bytes]:
        self.calls.append(("generate_data_key", kwargs))
        return {"Plaintext": b"k" * DEK_BYTES, "CiphertextBlob": b"wrapped-blob"}

    def decrypt(self, **kwargs: Any) -> dict[str, bytes]:
        self.calls.append(("decrypt", kwargs))
        return {"Plaintext": b"k" * DEK_BYTES}


def _arns() -> dict[KeyClass, str]:
    return {c: f"arn:aws:kms:ap-south-1:111122223333:key/{c.value}" for c in KeyClass}


def test_kms_requires_a_cmk_for_every_class() -> None:
    """A half-configured deployment must not start.

    Otherwise the first request touching the unconfigured class fails in
    production instead of at boot.
    """
    partial = {KeyClass.IDENTITY: "arn:aws:kms:ap-south-1:111122223333:key/identity"}
    with pytest.raises(KeyProviderError, match="no CMK configured"):
        KmsKeyProvider(partial, client=_StubKms())


def test_kms_sends_encryption_context() -> None:
    """The encryption context is both KMS-side AAD and the CloudTrail record.

    Without it, a blob wrapped for one class could be decrypted as another, and
    "who decrypted identity keys" would be unanswerable.
    """
    stub = _StubKms()
    KmsKeyProvider(_arns(), client=stub).generate_data_key(KeyClass.IDENTITY)

    name, kwargs = stub.calls[0]
    assert name == "generate_data_key"
    assert kwargs["EncryptionContext"] == {"key_class": "identity"}
    assert kwargs["KeySpec"] == "AES_256"


def test_kms_decrypt_pins_key_and_context() -> None:
    stub = _StubKms()
    KmsKeyProvider(_arns(), client=stub).unwrap_data_key(b"blob", KeyClass.RESUME_FILES)

    name, kwargs = stub.calls[0]
    assert name == "decrypt"
    assert kwargs["EncryptionContext"] == {"key_class": "resume_files"}
    # Pinning KeyId stops a forged blob selecting a different CMK.
    assert kwargs["KeyId"].endswith("resume_files")


def test_kms_errors_are_wrapped() -> None:
    class Broken:
        def generate_data_key(self, **_: Any) -> dict[str, bytes]:
            raise RuntimeError("throttled")

    with pytest.raises(KeyProviderError, match="GenerateDataKey"):
        KmsKeyProvider(_arns(), client=Broken()).generate_data_key(KeyClass.LOGS)
