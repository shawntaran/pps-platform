"""PII detection and redaction, run before anything leaves our boundary.

This package is what makes the rest of the privacy design work. The residency
argument in docs/privacy/infra-residency-and-latency.md rests on it: if the
text we send carries no direct identifiers, the LLM call is not a transfer of
identifiable personal data. If redaction fails, region pinning does not save
us -- we would be shipping the same data abroad with extra steps.

Usage::

    from pps_privacy.redaction import Redactor, KnownValues

    redactor = Redactor()              # build once per worker, not per request
    known = KnownValues(name=..., emails=(...,), phones=(...,))
    result = redactor.redact(resume_text, known)

    result.text            # safe to send onward
    result.entity_counts   # safe to log: counts, never values
    result.version         # record on the analysis row

It pseudonymises rather than anonymises. The output is still personal data in
the legal sense, so say "personal details removed", never "anonymous".
"""

from .entities import NEVER_STORE, REDACTION_VERSION, EntityType, RedactionResult, Span
from .known_values import KnownValueRecognizer, KnownValues
from .pipeline import RedactionError, Redactor, redact
from .recognizers import BUILTIN_RECOGNIZERS, RegexRecognizer, verhoeff_valid

__all__ = [
    "BUILTIN_RECOGNIZERS",
    "NEVER_STORE",
    "REDACTION_VERSION",
    "EntityType",
    "KnownValueRecognizer",
    "KnownValues",
    "RedactionError",
    "RedactionResult",
    "Redactor",
    "RegexRecognizer",
    "Span",
    "redact",
    "verhoeff_valid",
]
