"""Scrub the values we already know belong to this student.

The cheapest high-recall layer we have, and the one most often left out. We
hold the account holder's name, email and phone in the identity zone, so for
their own resume we are not guessing -- we can match exactly.

This catches what statistical detection misses: a name in ALL CAPS, split
across a table cell, written surname-first, or sitting in a document header
where there is no sentence structure for a model to work with.

It is a supplement, never the whole answer. A resume also contains referees,
previous managers and the student's own alternate addresses, none of which are
in our account record -- that is what the pattern and NER layers are for.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass

from .entities import EntityType, Span

__all__ = ["KnownValues", "KnownValueRecognizer"]

# Name fragments shorter than this are skipped. Many South Asian names contain
# short particles, and redacting a three-letter token across a whole document
# damages far more text than it protects.
_MIN_NAME_PART = 4

# Common honorifics and suffixes that are not the name itself.
_NAME_NOISE = frozenset(
    {"mr", "mrs", "ms", "miss", "dr", "prof", "shri", "smt", "kumari", "md", "jr", "sr"}
)


@dataclass(frozen=True)
class KnownValues:
    """What we hold about the person this document belongs to.

    Supplied by the caller from the identity zone, decrypted for the duration
    of one redaction job and never persisted alongside the result.
    """

    name: str | None = None
    emails: tuple[str, ...] = ()
    phones: tuple[str, ...] = ()
    student_ref: str | None = None


def _name_variants(name: str) -> list[str]:
    """Full name first, then the individual parts worth matching on.

    Ordering matters: the pipeline resolves overlaps by length, so offering the
    full name as its own candidate means "Priya Sharma" is redacted as one
    span rather than two adjacent ones.
    """
    cleaned = re.sub(r"\s+", " ", name).strip()
    if not cleaned:
        return []

    variants = [cleaned]
    parts = [
        p
        for p in re.split(r"[\s,]+", cleaned)
        if len(p) >= _MIN_NAME_PART and p.lower().strip(".") not in _NAME_NOISE
    ]
    # Surname-first is common on Indian academic records.
    if len(parts) >= 2:
        variants.append(f"{parts[-1]} {parts[0]}")
    variants.extend(parts)

    seen: set[str] = set()
    out = []
    for v in variants:
        key = v.lower()
        if key not in seen:
            seen.add(key)
            out.append(v)
    return out


def _phone_pattern(phone: str) -> str | None:
    """Match a phone number however it happens to be punctuated.

    The account record holds one canonical form; the resume might write the
    same number with spaces, dashes, brackets or a country code. Matching on
    the significant digits with optional separators between them covers all of
    those without a combinatorial list of formats.
    """
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return None
    # Ignore a leading country code so +91 98765 43210 still matches 9876543210.
    core = digits[-10:] if len(digits) > 10 else digits
    body = r"[\s\-.()]*".join(re.escape(d) for d in core)
    # Consume a country code if the document writes one, so the span covers the
    # whole number. Without this the digits are replaced but a stranded "+91"
    # is left behind -- not sensitive in itself, but it reveals the country and
    # it looks like a bug to anyone reading the redacted text.
    return r"(?:\+\s?\d{1,3}[\s\-.]*)?" + body


class KnownValueRecognizer:
    """Finds the account holder's own details in their document."""

    name = "known_values"

    def __init__(self, known: KnownValues) -> None:
        self._rules: list[tuple[re.Pattern[str], EntityType]] = []

        for variant in _name_variants(known.name or ""):
            self._rules.append(
                (re.compile(rf"\b{re.escape(variant)}\b", re.IGNORECASE), EntityType.PERSON)
            )

        for email in known.emails:
            if not email.strip():
                continue
            self._rules.append(
                (re.compile(rf"\b{re.escape(email.strip())}\b", re.IGNORECASE), EntityType.EMAIL)
            )
            # The local part alone often appears as a username or handle.
            local = email.split("@", 1)[0]
            if len(local) >= _MIN_NAME_PART:
                self._rules.append(
                    (re.compile(rf"\b{re.escape(local)}\b", re.IGNORECASE), EntityType.EMAIL)
                )

        for phone in known.phones:
            pattern = _phone_pattern(phone)
            if pattern:
                self._rules.append((re.compile(pattern), EntityType.PHONE))

        if known.student_ref and len(known.student_ref) >= _MIN_NAME_PART:
            self._rules.append(
                (
                    re.compile(rf"\b{re.escape(known.student_ref)}\b", re.IGNORECASE),
                    EntityType.STUDENT_REF,
                )
            )

    def find(self, text: str) -> Iterator[Span]:
        for pattern, entity in self._rules:
            for match in pattern.finditer(text):
                if match.end() > match.start():
                    # Confidence 1.0: this is not inference. We are matching a
                    # value we already hold for this person.
                    yield Span(match.start(), match.end(), entity, 1.0, self.name)
