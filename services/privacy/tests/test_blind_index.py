"""Tests for blind-index lookup on encrypted columns."""

from __future__ import annotations

import os

import pytest

from pps_privacy.crypto import INDEX_KEY_BYTES, IndexDomain, blind_index, matches, normalise

KEY = os.urandom(INDEX_KEY_BYTES)
OTHER_KEY = os.urandom(INDEX_KEY_BYTES)


def idx(value: str, key: bytes = KEY, domain: IndexDomain = IndexDomain.EMAIL) -> str:
    return blind_index(value, key, domain=domain)


def test_is_deterministic() -> None:
    # Without this there is no lookup at all.
    assert idx("priya@example.edu") == idx("priya@example.edu")


def test_different_values_differ() -> None:
    assert idx("priya@example.edu") != idx("arjun@example.edu")


def test_case_and_whitespace_are_normalised() -> None:
    """Students type their address inconsistently; the index must not care."""
    assert idx("  Priya@Example.EDU  ") == idx("priya@example.edu")


def test_unicode_variants_are_normalised() -> None:
    """NFKC folding.

    A full-width character renders almost identically to its ASCII form. Without
    NFKC, someone could register a visually identical duplicate account and slip
    past a uniqueness check on the index.
    """
    assert idx("ｐriya@example.edu") == idx("priya@example.edu")


def test_domains_are_separated() -> None:
    """The same string in two columns must not produce the same index.

    Otherwise a number held both as a primary phone and as a recovery contact
    links those columns for anyone reading them.
    """
    value = "+919876543210"
    assert blind_index(value, KEY, domain=IndexDomain.PHONE) != blind_index(
        value, KEY, domain=IndexDomain.STUDENT_REF
    )


def test_institutional_and_personal_email_are_separated() -> None:
    value = "priya@example.edu"
    assert blind_index(value, KEY, domain=IndexDomain.EMAIL) != blind_index(
        value, KEY, domain=IndexDomain.INSTITUTIONAL_EMAIL
    )


def test_index_depends_on_the_key() -> None:
    """A stolen database without the key yields nothing searchable."""
    assert idx("priya@example.edu", KEY) != idx("priya@example.edu", OTHER_KEY)


def test_equality_leak_is_real_and_intended() -> None:
    """Documents the accepted tradeoff rather than pretending it is absent.

    Two accounts sharing an address are visibly linked in the index column. We
    accept that in exchange for being able to look a user up; anyone changing
    this design should know they are changing a documented property.
    """
    assert idx("shared@example.edu") == idx("SHARED@example.edu")


def test_short_key_is_rejected() -> None:
    # A short key would produce a valid-looking index with no strength behind it.
    with pytest.raises(ValueError, match="at least"):
        idx("priya@example.edu", os.urandom(INDEX_KEY_BYTES - 1))


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_empty_value_is_rejected(value: str) -> None:
    """An all-whitespace value normalises to empty; indexing it would make
    every such row collide on one index."""
    with pytest.raises(ValueError, match="empty"):
        idx(value)


def test_output_is_hex_sha256() -> None:
    result = idx("priya@example.edu")
    assert len(result) == 64
    assert set(result) <= set("0123456789abcdef")


def test_matches_accepts_the_right_value() -> None:
    stored = idx("priya@example.edu")
    assert matches("  PRIYA@example.edu ", stored, KEY, domain=IndexDomain.EMAIL)


def test_matches_rejects_wrong_value_key_and_domain() -> None:
    stored = idx("priya@example.edu")
    assert not matches("arjun@example.edu", stored, KEY, domain=IndexDomain.EMAIL)
    assert not matches("priya@example.edu", stored, OTHER_KEY, domain=IndexDomain.EMAIL)
    assert not matches("priya@example.edu", stored, KEY, domain=IndexDomain.PHONE)


def test_normalise_is_exposed_for_callers() -> None:
    # Callers writing a uniqueness check need the same canonical form we index.
    assert normalise("  Priya@Example.EDU ") == "priya@example.edu"
