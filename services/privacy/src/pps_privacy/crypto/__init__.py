"""Cryptographic primitives for the privacy layer.

Three pieces that work together:

- :mod:`envelope` -- AES-256-GCM, with every ciphertext bound to its location
  so it cannot be moved between rows, columns or users.
- :mod:`keyprovider` -- per-record data keys wrapped by a KMS-held key, which
  is what makes crypto-shredding (and therefore real erasure) possible.
- :mod:`blind_index` -- equality lookup on an encrypted column.

Import from this package rather than the submodules, so the surface stays small
and there is one place to audit what the privacy layer exposes.
"""

from .blind_index import INDEX_KEY_BYTES, IndexDomain, blind_index, matches, normalise
from .envelope import (
    DEK_BYTES,
    VERSION,
    CryptoError,
    DecryptionError,
    decrypt,
    decrypt_text,
    encrypt,
    encrypt_text,
    field_aad,
    file_aad,
    wrap_aad,
)
from .keyprovider import (
    DataKey,
    KeyClass,
    KeyProvider,
    KeyProviderError,
    KmsKeyProvider,
    LocalKeyProvider,
)

__all__ = [
    "DEK_BYTES",
    "INDEX_KEY_BYTES",
    "VERSION",
    "CryptoError",
    "DataKey",
    "DecryptionError",
    "IndexDomain",
    "KeyClass",
    "KeyProvider",
    "KeyProviderError",
    "KmsKeyProvider",
    "LocalKeyProvider",
    "blind_index",
    "decrypt",
    "decrypt_text",
    "encrypt",
    "encrypt_text",
    "field_aad",
    "file_aad",
    "matches",
    "normalise",
    "wrap_aad",
]
