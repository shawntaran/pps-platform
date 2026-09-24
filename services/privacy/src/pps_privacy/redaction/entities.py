"""What we detect, and what we record about each detection.

Terminology, because the distinction is load-bearing and easy to blur: this
module *pseudonymises*. It replaces identifiers with stable placeholders and
keeps the mapping out of band. It does not anonymise -- the original text is
still recoverable from our own records, so redacted output remains personal
data in the legal sense even though it carries no visible identifiers.

UI copy and documentation must say "personal details removed", never
"anonymous". See the ground rules in docs/privacy/phase1-notes.md section 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = ["EntityType", "Span", "RedactionResult", "REDACTION_VERSION"]

# Recorded on every analysis row. If a leak is ever found we need to know which
# build of the detector produced a given redaction, and which documents to
# reprocess. Bump this whenever detection behaviour changes.
REDACTION_VERSION = "1.0.0"


class EntityType(str, Enum):
    """Categories of thing we take out of a resume before it leaves our boundary.

    Split into three groups by what happens to them, not by what they are:

    * **Vault** -- identifies the student directly. Removed from the text and
      kept encrypted in the identity zone, because we need it for login and for
      consented recruiter reveals.
    * **Drop** -- we never want it at all. Removed and not stored anywhere,
      either because it is a protected characteristic, or because it belongs to
      a third party who never agreed to anything.
    * **Coarsen** -- useful for analysis at lower precision. Replaced with a
      placeholder rather than deleted outright.
    """

    # Vault
    PERSON = "PERSON"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ADDRESS = "ADDRESS"
    URL_PROFILE = "URL_PROFILE"          # LinkedIn, GitHub, portfolio: the handle is the name

    # Drop: protected characteristics and government identifiers.
    # A resume should never carry these, and we tell students so -- but they
    # routinely do, especially on templates popular in India.
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    GENDER = "GENDER"
    MARITAL_STATUS = "MARITAL_STATUS"
    NATIONALITY = "NATIONALITY"
    RELIGION = "RELIGION"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    PASSPORT = "PASSPORT"
    GOVERNMENT_ID = "GOVERNMENT_ID"

    # Drop: third-party personal data. A referee never consented to us
    # processing their details, so they are removed regardless of consent.
    REFEREE = "REFEREE"

    # Coarsen
    EMPLOYER = "EMPLOYER"
    INSTITUTION = "INSTITUTION"
    STUDENT_REF = "STUDENT_REF"          # roll number, registration number


#: Types that must never survive into text sent to a third party, and must not
#: be stored either. Everything here is removed even when the student consented
#: to AI processing -- consent does not make it necessary, and Art. 5(1)(c)
#: minimisation applies regardless.
NEVER_STORE: frozenset[EntityType] = frozenset(
    {
        EntityType.DATE_OF_BIRTH,
        EntityType.GENDER,
        EntityType.MARITAL_STATUS,
        EntityType.NATIONALITY,
        EntityType.RELIGION,
        EntityType.AADHAAR,
        EntityType.PAN,
        EntityType.PASSPORT,
        EntityType.GOVERNMENT_ID,
        EntityType.REFEREE,
    }
)


@dataclass(frozen=True, order=True)
class Span:
    """One detected entity, as a half-open character range ``[start, end)``.

    ``confidence`` drives overlap resolution, not a decision about whether to
    redact: anything detected is redacted. A deterministic recogniser (a
    checksummed Aadhaar number, or an exact match against the account holder's
    own email) scores 1.0; statistical name detection scores lower because it
    genuinely is less certain.
    """

    start: int
    end: int
    entity: EntityType = field(compare=False)
    confidence: float = field(default=1.0, compare=False)
    detector: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f"invalid span [{self.start}, {self.end})")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence out of range: {self.confidence}")

    @property
    def length(self) -> int:
        return self.end - self.start

    def overlaps(self, other: Span) -> bool:
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class RedactionResult:
    """Redacted text plus everything needed to audit the decision later.

    Deliberately does **not** carry the original text or the values that were
    removed. Returning those alongside the redacted output makes it far too
    easy for a caller to log the wrong field, and a log of what we redacted is
    a second copy of exactly the data we were protecting.
    """

    text: str
    spans: tuple[Span, ...]
    version: str = REDACTION_VERSION

    @property
    def entity_counts(self) -> dict[str, int]:
        """How many of each type were removed. Safe to log -- counts, not values."""
        counts: dict[str, int] = {}
        for span in self.spans:
            counts[span.entity.value] = counts.get(span.entity.value, 0) + 1
        return counts

    @property
    def found_prohibited(self) -> tuple[EntityType, ...]:
        """Types the student should be warned about having included.

        Drives the "your resume contained a government ID, we removed it"
        message. Telling them is both good practice and a nudge toward not
        sending the next one.
        """
        seen = {s.entity for s in self.spans if s.entity in NEVER_STORE}
        return tuple(sorted(seen, key=lambda e: e.value))
