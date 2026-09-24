"""Tests for AES-256-GCM field/file encryption.

Each test names the property it protects. The AAD-binding tests are the
important ones: they are what stops a ciphertext being moved between users.
"""

from __future__ import annotations

import os

import pytest

from pps_privacy.crypto import (
    DEK_BYTES,
    CryptoError,
    DecryptionError,
    decrypt,
    decrypt_text,
    encrypt,
    encrypt_text,
    field_aad,
    file_aad,
)

ALICE = field_aad("users", "name_enc", "user-1")
BOB = field_aad("users", "name_enc", "user-2")


@pytest.fixture
def dek() -> bytes:
    return os.urandom(DEK_BYTES)


def test_round_trip(dek: bytes) -> None:
    token = encrypt(b"Priya Sharma", dek, ALICE)
    assert decrypt(token, dek, ALICE) == b"Priya Sharma"


def test_round_trip_text_handles_non_ascii(dek: bytes) -> None:
    # Names are not ASCII. If this breaks, we corrupt real students' records.
    name = "Ananya Krishnan"
    token = encrypt_text(name, dek, ALICE)
    assert decrypt_text(token, dek, ALICE) == name


def test_empty_plaintext_round_trips(dek: bytes) -> None:
    # An optional phone number is a legitimately empty field.
    assert decrypt(encrypt(b"", dek, ALICE), dek, ALICE) == b""


def test_same_plaintext_encrypts_differently(dek: bytes) -> None:
    """Randomised nonce: equal plaintexts must not produce equal ciphertexts.

    If they did, anyone reading the column could tell which students share a
    name or an address without decrypting anything.
    """
    a = encrypt(b"same", dek, ALICE)
    b = encrypt(b"same", dek, ALICE)
    assert a != b
    assert decrypt(a, dek, ALICE) == decrypt(b, dek, ALICE) == b"same"


def test_wrong_key_fails(dek: bytes) -> None:
    token = encrypt(b"secret", dek, ALICE)
    with pytest.raises(DecryptionError):
        decrypt(token, os.urandom(DEK_BYTES), ALICE)


def test_ciphertext_cannot_be_moved_to_another_user(dek: bytes) -> None:
    """The property that makes AAD worth having.

    A bug (or a malicious UPDATE) that copies Alice's encrypted name into Bob's
    row must not yield a readable name. Without AAD binding it would.
    """
    token = encrypt(b"Priya Sharma", dek, ALICE)
    with pytest.raises(DecryptionError):
        decrypt(token, dek, BOB)


def test_ciphertext_cannot_be_moved_to_another_column(dek: bytes) -> None:
    email_aad = field_aad("users", "email_enc", "user-1")
    token = encrypt(b"priya@example.edu", dek, email_aad)
    phone_aad = field_aad("users", "phone_enc", "user-1")
    with pytest.raises(DecryptionError):
        decrypt(token, dek, phone_aad)


def test_field_and_file_aad_do_not_collide(dek: bytes) -> None:
    token = encrypt(b"x", dek, field_aad("a", "b", "c"))
    with pytest.raises(DecryptionError):
        decrypt(token, dek, file_aad("a", "b", "c"))


def test_aad_components_are_unambiguous(dek: bytes) -> None:
    """Length-prefixing, not separators.

    ("users", "ab", "c") and ("users", "a", "bc") must be different AADs. A
    naive "join with a delimiter" encoding collides here.
    """
    token = encrypt(b"x", dek, field_aad("users", "ab", "c"))
    with pytest.raises(DecryptionError):
        decrypt(token, dek, field_aad("users", "a", "bc"))


def test_tampered_ciphertext_fails(dek: bytes) -> None:
    token = bytearray(encrypt(b"balance: 100", dek, ALICE))
    token[-1] ^= 0x01  # flip one bit of the GCM tag
    with pytest.raises(DecryptionError):
        decrypt(bytes(token), dek, ALICE)


def test_tampered_body_fails(dek: bytes) -> None:
    token = bytearray(encrypt(b"role: student", dek, ALICE))
    token[20] ^= 0xFF
    with pytest.raises(DecryptionError):
        decrypt(bytes(token), dek, ALICE)


def test_truncated_token_fails(dek: bytes) -> None:
    token = encrypt(b"secret", dek, ALICE)
    with pytest.raises(DecryptionError):
        decrypt(token[:10], dek, ALICE)


def test_unknown_version_is_rejected(dek: bytes) -> None:
    """A future format change must fail loudly, not be misparsed as v1."""
    token = bytearray(encrypt(b"secret", dek, ALICE))
    token[0] = 0x99
    with pytest.raises(DecryptionError, match="version"):
        decrypt(bytes(token), dek, ALICE)


def test_aad_is_required(dek: bytes) -> None:
    # Forgetting AAD silently removes the binding, so make it impossible.
    with pytest.raises(CryptoError, match="aad"):
        encrypt(b"x", dek, b"")


@pytest.mark.parametrize("size", [0, 16, 31, 33, 64])
def test_wrong_key_size_is_rejected(size: int) -> None:
    with pytest.raises(CryptoError, match="32 bytes"):
        encrypt(b"x", os.urandom(size), ALICE)


def test_failure_reason_is_not_disclosed(dek: bytes) -> None:
    """Wrong key and wrong AAD must be indistinguishable to a caller.

    Distinguishing them tells a prober whether they hold the right key, which
    turns one unknown into two separate, easier searches.
    """
    token = encrypt(b"secret", dek, ALICE)

    with pytest.raises(DecryptionError) as wrong_key:
        decrypt(token, os.urandom(DEK_BYTES), ALICE)
    with pytest.raises(DecryptionError) as wrong_aad:
        decrypt(token, dek, BOB)

    assert str(wrong_key.value) == str(wrong_aad.value)
