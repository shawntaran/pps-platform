"""AES-256-GCM encryption for fields and files.

Every ciphertext this module produces is bound to *where it lives* via GCM's
additional authenticated data (AAD). Moving a ciphertext from one column, row or
user to another makes it undecryptable rather than silently readable -- so a SQL
bug or a malicious UPDATE that copies `name_enc` between rows fails loudly.

Wire format (version 1)::

    b"\x01" || nonce (12 bytes) || ciphertext || GCM tag (16 bytes)

The leading version byte exists so a future algorithm change is unambiguous
rather than a guess based on length.

Erasure model: data is destroyed by destroying the per-user data key that
encrypted it (crypto-shredding), which reaches copies we cannot reach directly --
S3 object versions, RDS snapshots, backups. Deleting rows is a complement to
that, not a substitute for it.
"""

from __future__ import annotations

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = [
    "VERSION",
    "DEK_BYTES",
    "CryptoError",
    "DecryptionError",
    "encrypt",
    "decrypt",
    "field_aad",
    "file_aad",
    "wrap_aad",
]

VERSION = 1
_VERSION_BYTE = bytes([VERSION])

DEK_BYTES = 32  # AES-256
NONCE_BYTES = 12  # 96-bit nonce, the GCM-recommended size
TAG_BYTES = 16

_MIN_TOKEN = 1 + NONCE_BYTES + TAG_BYTES


class CryptoError(Exception):
    """Base class for this module's failures."""


class DecryptionError(CryptoError):
    """Ciphertext could not be authenticated or decrypted.

    Raised for a wrong key, a wrong AAD (data moved to another column, row or
    user), a tampered ciphertext, or a truncated token. The cases are
    deliberately not distinguished: telling a caller *why* decryption failed
    leaks information to anyone able to probe it.
    """


def _length_prefixed(*parts: str) -> bytes:
    """Join parts so no two different inputs can produce the same bytes.

    ``("ab", "c")`` and ``("a", "bc")`` must not collide, which a plain
    separator (``"ab|c"`` vs ``"a|bc"`` is fine, but ``"a|b", "c"`` vs
    ``"a", "b|c"`` is not) cannot guarantee once a part may contain the
    separator. Length prefixes make the encoding injective without needing to
    validate or escape the inputs.
    """
    out = bytearray()
    for part in parts:
        raw = part.encode("utf-8")
        out += len(raw).to_bytes(4, "big")
        out += raw
    return bytes(out)


def field_aad(table: str, column: str, row_id: str) -> bytes:
    """AAD binding a field ciphertext to one column of one row.

    ``row_id`` is whatever identifies the row (``user_id``, ``resume_id``).
    Pass it as text; a UUID's string form is fine and stable.
    """
    return _length_prefixed("field", table, column, str(row_id))


def file_aad(bucket: str, key: str, owner_id: str) -> bytes:
    """AAD binding a file ciphertext to one object and its owner."""
    return _length_prefixed("file", bucket, key, str(owner_id))


def encrypt(plaintext: bytes, dek: bytes, aad: bytes) -> bytes:
    """Encrypt ``plaintext`` under ``dek``, bound to ``aad``.

    A fresh random nonce is drawn per call, so encrypting the same plaintext
    twice yields different ciphertexts. Never reuse a (key, nonce) pair -- with
    GCM that breaks confidentiality *and* authentication, so there is no
    caller-supplied nonce parameter by design.
    """
    if len(dek) != DEK_BYTES:
        raise CryptoError(f"data key must be {DEK_BYTES} bytes, got {len(dek)}")
    if not aad:
        raise CryptoError("aad is required; use field_aad() or file_aad()")

    nonce = os.urandom(NONCE_BYTES)
    sealed = AESGCM(dek).encrypt(nonce, plaintext, aad)
    return _VERSION_BYTE + nonce + sealed


def decrypt(token: bytes, dek: bytes, aad: bytes) -> bytes:
    """Reverse :func:`encrypt`. Raises :class:`DecryptionError` on any failure."""
    if len(dek) != DEK_BYTES:
        raise CryptoError(f"data key must be {DEK_BYTES} bytes, got {len(dek)}")
    if len(token) < _MIN_TOKEN:
        raise DecryptionError("ciphertext is truncated")
    if token[0] != VERSION:
        raise DecryptionError(f"unsupported ciphertext version {token[0]}")

    nonce = token[1 : 1 + NONCE_BYTES]
    sealed = token[1 + NONCE_BYTES :]
    try:
        return AESGCM(dek).decrypt(nonce, sealed, aad)
    except InvalidTag as exc:
        raise DecryptionError("ciphertext failed authentication") from exc


def encrypt_text(plaintext: str, dek: bytes, aad: bytes) -> bytes:
    """UTF-8 convenience wrapper over :func:`encrypt`."""
    return encrypt(plaintext.encode("utf-8"), dek, aad)


def decrypt_text(token: bytes, dek: bytes, aad: bytes) -> str:
    """UTF-8 convenience wrapper over :func:`decrypt`."""
    return decrypt(token, dek, aad).decode("utf-8")


def wrap_aad(key_class: str) -> bytes:
    """AAD binding a wrapped data key to its key class.

    Keeps every AAD construction in this one module, so there is a single place
    to audit what each ciphertext is bound to. A data key wrapped for
    ``resume_files`` cannot be unwrapped as an ``identity`` key.
    """
    return _length_prefixed("wrap", key_class)
