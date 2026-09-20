"""Blind indexes: looking up an encrypted column without decrypting it.

We encrypt emails and phone numbers, which means ``WHERE email = ?`` no longer
works -- AES-GCM is randomised, so the same address encrypts differently every
time. A blind index solves it: store ``HMAC-SHA256(index_key, normalised value)``
in a second column and query on that instead.

What this deliberately leaks, and why it is acceptable
------------------------------------------------------
A blind index reveals *equality*. Two rows with the same email have the same
index, so anyone who can read the column learns which accounts share an address
even though they cannot read the address. That is the price of being able to
look a user up at all, and it is a far smaller leak than storing the value in
plaintext.

What it must not leak
---------------------
The index key is the whole defence. If it leaks, the index becomes a rainbow
table: an attacker with the column and the key can test candidate emails
offline and recover every address. So:

- The index key lives in AWS Secrets Manager, NOT in the database. An attacker
  who exfiltrates a database dump must still get the key from somewhere else.
- It is a *different* key from any data-encryption key. Reusing a DEK here would
  mean one compromise breaks both confidentiality and lookup.
- Rotating it requires recomputing every index, which needs the plaintexts, so
  treat rotation as a planned migration rather than an operational knob.

Normalisation
-------------
Inputs are Unicode-normalised, stripped and case-folded so that
``" Alice@Example.COM "`` and ``"alice@example.com"`` find the same row.
Phone numbers must be canonicalised to E.164 by the caller first -- this module
will not guess a country code, and ``+91 98765 43210`` and ``09876543210``
would otherwise produce different indexes for the same person.
"""

from __future__ import annotations

import hashlib
import hmac
import unicodedata
from enum import Enum

__all__ = ["IndexDomain", "INDEX_KEY_BYTES", "blind_index", "matches", "normalise"]

INDEX_KEY_BYTES = 32


class IndexDomain(str, Enum):
    """Domain separation, so identical values in different columns differ.

    Without it, a phone number stored as a recovery contact and the same number
    stored as a primary phone would produce the same index, needlessly linking
    two columns that should be independent.
    """

    EMAIL = "email"
    INSTITUTIONAL_EMAIL = "institutional_email"
    PHONE = "phone"
    STUDENT_REF = "student_ref"


def normalise(value: str) -> str:
    """Canonical form used before hashing.

    NFKC folds visually identical Unicode variants together, so a full-width
    character cannot be used to sneak a duplicate account past a uniqueness
    check on the index.
    """
    return unicodedata.normalize("NFKC", value).strip().casefold()


def blind_index(value: str, key: bytes, *, domain: IndexDomain) -> str:
    """Return the hex blind index of ``value`` for ``domain``.

    Raises ``ValueError`` on an empty value or an undersized key -- both are
    configuration mistakes that would otherwise produce a valid-looking index
    with no security behind it.
    """
    if len(key) < INDEX_KEY_BYTES:
        raise ValueError(f"index key must be at least {INDEX_KEY_BYTES} bytes")

    canonical = normalise(value)
    if not canonical:
        raise ValueError("cannot index an empty value")

    # Length-prefixed so ("email", "a@b") cannot collide with ("emaila", "@b").
    domain_bytes = domain.value.encode("utf-8")
    payload = (
        len(domain_bytes).to_bytes(4, "big")
        + domain_bytes
        + canonical.encode("utf-8")
    )
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def matches(value: str, stored_index: str, key: bytes, *, domain: IndexDomain) -> bool:
    """Constant-time comparison of a candidate value against a stored index.

    Uses :func:`hmac.compare_digest` rather than ``==``: a plain comparison
    short-circuits on the first differing byte, which is measurable and lets an
    attacker recover a valid index one byte at a time.
    """
    return hmac.compare_digest(blind_index(value, key, domain=domain), stored_index)
