"""Deterministic detectors: the layer that does the heavy lifting.

Statistical name detection gets the attention, but on real resumes most
identifiers are found by pattern and by exact match. This layer is where recall
actually comes from, and unlike a model it does not silently get worse on a
document format it has not seen.

Design rule: prefer a validated pattern over a loose one. A bare
twelve-digit-number regex flags every order number and transaction ID in the
document; the same regex gated on the Aadhaar checksum almost never fires by
accident. Over-redaction is not free -- it degrades the analysis the student
came for, and it trains reviewers to ignore the warnings.

Indian formats are first-class here. The team and the students are in India
(pending confirmation, see docs/privacy/infra-residency-and-latency.md section 2),
and Presidio's stock recognisers do not cover Aadhaar, PAN or Indian phone
conventions.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Protocol

from .entities import EntityType, Span

__all__ = ["Recognizer", "RegexRecognizer", "BUILTIN_RECOGNIZERS", "verhoeff_valid"]


class Recognizer(Protocol):
    """Anything that can point at entities in text.

    Regex rules, the known-value scrubber and the optional NER adapter all
    satisfy this, so the pipeline treats them uniformly and the layers can be
    reordered or disabled without touching orchestration.
    """

    name: str

    def find(self, text: str) -> Iterable[Span]:  # pragma: no cover - protocol
        ...


# --- Verhoeff, for Aadhaar -------------------------------------------------
# Aadhaar numbers carry a Verhoeff check digit. Validating it turns "any twelve
# digits" into something that essentially only fires on real Aadhaar numbers,
# which is the difference between a usable detector and one that shreds every
# numeric identifier in the document.

_VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)


def verhoeff_valid(digits: str) -> bool:
    """True if ``digits`` passes the Verhoeff checksum used by Aadhaar."""
    check = 0
    for i, ch in enumerate(reversed(digits)):
        if not ch.isdigit():
            return False
        check = _VERHOEFF_D[check][_VERHOEFF_P[i % 8][int(ch)]]
    return check == 0


class RegexRecognizer:
    """A pattern, an entity type, and an optional validator.

    ``group`` selects which capture group is the sensitive part, so a rule can
    match ``DOB: 1999-04-02`` for context but redact only the date -- keeping
    the label makes the redacted text readable, which helps the analysis.
    """

    def __init__(
        self,
        name: str,
        pattern: str,
        entity: EntityType,
        *,
        confidence: float = 0.95,
        group: int = 0,
        validator=None,
        flags: int = re.IGNORECASE,
    ) -> None:
        self.name = name
        self.entity = entity
        self.confidence = confidence
        self.group = group
        self.validator = validator
        self._re = re.compile(pattern, flags)

    def find(self, text: str) -> Iterator[Span]:
        for match in self._re.finditer(text):
            value = match.group(self.group)
            if self.validator is not None and not self.validator(value):
                continue
            start, end = match.span(self.group)
            yield Span(start, end, self.entity, self.confidence, self.name)


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _aadhaar_ok(value: str) -> bool:
    d = _digits(value)
    # Real Aadhaar numbers never start 0 or 1, on top of the checksum.
    return len(d) == 12 and d[0] not in "01" and verhoeff_valid(d)


def _pan_ok(value: str) -> bool:
    # AAAAA9999A, where the 4th character encodes holder type and the 5th is
    # the surname initial. Checking the shape alone is enough to be confident.
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value.upper()))


BUILTIN_RECOGNIZERS: tuple[Recognizer, ...] = (
    # --- direct identifiers ---
    RegexRecognizer(
        "email",
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        EntityType.EMAIL,
        confidence=1.0,
    ),
    RegexRecognizer(
        "phone_india",
        r"(?:(?:\+|00)?91[\s\-.]?)?\b[6-9]\d{4}[\s\-.]?\d{5}\b",
        EntityType.PHONE,
        confidence=0.9,
    ),
    RegexRecognizer(
        "phone_intl",
        r"\+\d{1,3}[\s\-.]?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}\b",
        EntityType.PHONE,
        confidence=0.85,
    ),
    # A LinkedIn or GitHub handle is usually the person's name, so these are
    # identifiers rather than harmless links.
    RegexRecognizer(
        "linkedin",
        r"\b(?:https?://)?(?:[a-z]{2,3}\.)?linkedin\.com/(?:in|pub)/[A-Za-z0-9\-_%]+/?",
        EntityType.URL_PROFILE,
        confidence=1.0,
    ),
    RegexRecognizer(
        "github",
        r"\b(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9\-_]+/?",
        EntityType.URL_PROFILE,
        confidence=1.0,
    ),
    # --- government identifiers: validated, so false positives are rare ---
    RegexRecognizer(
        "aadhaar",
        r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
        EntityType.AADHAAR,
        confidence=1.0,
        validator=_aadhaar_ok,
    ),
    RegexRecognizer(
        "pan",
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        EntityType.PAN,
        confidence=1.0,
        validator=_pan_ok,
        flags=0,  # case-sensitive: PAN is always upper case, and lowering the
                  # bar here matches ordinary words plus digits
    ),
    RegexRecognizer(
        "passport_in",
        r"\b[A-PR-WY][0-9]{7}\b",
        EntityType.PASSPORT,
        confidence=0.7,
        flags=0,
    ),
    # --- protected characteristics, matched via their labels ---
    # Only the value is redacted; the label survives so the analysis can still
    # tell the student to remove the field.
    RegexRecognizer(
        "date_of_birth",
        r"(?:date\s+of\s+birth|d\.?o\.?b\.?|birth\s*date)\s*[:\-]?\s*"
        r"([0-9]{1,4}[/\-.][0-9]{1,2}[/\-.][0-9]{1,4}"
        r"|[0-9]{1,2}\s+[A-Za-z]{3,9},?\s+[0-9]{4}"
        r"|[A-Za-z]{3,9}\s+[0-9]{1,2},?\s+[0-9]{4})",
        EntityType.DATE_OF_BIRTH,
        confidence=1.0,
        group=1,
    ),
    RegexRecognizer(
        "gender",
        r"(?:gender|sex)\s*[:\-]\s*(male|female|man|woman|transgender|non[\s\-]?binary|other)\b",
        EntityType.GENDER,
        confidence=1.0,
        group=1,
    ),
    RegexRecognizer(
        "marital_status",
        r"(?:marital\s+status)\s*[:\-]\s*(single|married|unmarried|divorced|widowed|separated)\b",
        EntityType.MARITAL_STATUS,
        confidence=1.0,
        group=1,
    ),
    RegexRecognizer(
        "nationality",
        r"(?:nationality|citizenship)\s*[:\-]\s*([A-Za-z]+)",
        EntityType.NATIONALITY,
        confidence=1.0,
        group=1,
    ),
    RegexRecognizer(
        "religion",
        r"(?:religion|caste|community)\s*[:\-]\s*([A-Za-z]+)",
        EntityType.RELIGION,
        confidence=1.0,
        group=1,
    ),
    # Parent names are common on Indian resume templates and identify a family,
    # not just the student.
    RegexRecognizer(
        "parent_name",
        r"(?:father|mother|guardian)(?:'s)?\s+name\s*[:\-]\s*([^\n\r]{2,60})",
        EntityType.REFEREE,
        confidence=1.0,
        group=1,
    ),
    # --- student reference numbers ---
    RegexRecognizer(
        "student_ref",
        r"(?:roll|registration|reg|enrol(?:l)?ment|student)\s*(?:no\.?|number|id)?\s*[:\-]\s*([A-Za-z0-9\-/]{4,24})",
        EntityType.STUDENT_REF,
        confidence=0.95,
        group=1,
    ),
)
