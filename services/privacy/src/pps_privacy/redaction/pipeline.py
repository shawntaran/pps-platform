"""Orchestration: run the detection layers, then rewrite the text.

Layer order and why it is this order:

1. **Known values** -- exact matches against what we already hold for this
   student. Highest recall, zero inference, essentially free.
2. **Patterns** -- validated regex rules, including Indian government IDs.
3. **NER** -- optional and last, because it is the only probabilistic layer.
   It catches names we do not hold (referees, previous managers) at the cost of
   both misses and false positives.
4. **Output scan** -- the same detectors run over whatever the model returns,
   because a model given redacted text can still reconstruct an identifier from
   context, or echo one we missed.

The pipeline **fails closed**. If detection raises, nothing is returned and
nothing is sent onward. A redaction bug must never degrade into "send the raw
text and hope".

What this is not: a guarantee. Detection is imperfect, which is why the
provider contract, the eval harness and telling students not to include
sensitive data all still matter. See risk R4 in docs/privacy/phase1-notes.md.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .entities import REDACTION_VERSION, EntityType, RedactionResult, Span
from .known_values import KnownValueRecognizer, KnownValues
from .recognizers import BUILTIN_RECOGNIZERS, Recognizer

__all__ = ["Redactor", "RedactionError", "redact"]


class RedactionError(Exception):
    """Detection failed. The caller must not send anything onward."""


def _resolve_overlaps(spans: Iterable[Span]) -> list[Span]:
    """Pick a non-overlapping set, preferring confident then long matches.

    Overlaps are normal, not exceptional: a known-value name match and an NER
    name match cover the same words, and an email match sits inside a longer
    contact-line match. Taking the highest-confidence candidate first means a
    value we *know* beats a value we *inferred*; length breaks the remaining
    ties so "Priya Sharma" wins over "Priya".
    """
    ordered = sorted(spans, key=lambda s: (-s.confidence, -s.length, s.start))
    chosen: list[Span] = []
    for span in ordered:
        if not any(span.overlaps(kept) for kept in chosen):
            chosen.append(span)
    return sorted(chosen)


class Redactor:
    """Removes identifiers from text and replaces them with placeholders.

    Construct once per worker process and reuse. The regex rules compile at
    construction, and an NER model -- if one is attached -- must be loaded once
    at startup rather than per request: model loading is the single biggest
    latency trap in this pipeline (see the latency notes, section 6).
    """

    def __init__(self, recognizers: Sequence[Recognizer] | None = None) -> None:
        self._recognizers = tuple(recognizers if recognizers is not None else BUILTIN_RECOGNIZERS)

    def detect(self, text: str, known: KnownValues | None = None) -> list[Span]:
        """Run every layer and return the resolved, non-overlapping spans."""
        layers: list[Recognizer] = []
        if known is not None:
            # First, so exact matches win overlap resolution on equal footing.
            layers.append(KnownValueRecognizer(known))
        layers.extend(self._recognizers)

        found: list[Span] = []
        for recognizer in layers:
            try:
                found.extend(recognizer.find(text))
            except Exception as exc:  # noqa: BLE001 - any failure must fail closed
                raise RedactionError(
                    f"recogniser {getattr(recognizer, 'name', recognizer)!r} failed"
                ) from exc
        return _resolve_overlaps(found)

    def redact(self, text: str, known: KnownValues | None = None) -> RedactionResult:
        """Return ``text`` with every detected identifier replaced.

        Placeholders are stable within a document: the same email becomes
        ``[EMAIL_1]`` everywhere it appears. That preserves the coreference the
        analysis needs ("this address matches the one in the header") without
        preserving the value. Numbering restarts per document, so placeholders
        say nothing across documents.
        """
        if text is None:
            raise RedactionError("cannot redact None")

        spans = self.detect(text, known)

        # Same original value -> same placeholder, per entity type.
        assigned: dict[tuple[EntityType, str], str] = {}
        counters: dict[EntityType, int] = {}

        out: list[str] = []
        cursor = 0
        for span in spans:
            original = text[span.start : span.end]
            key = (span.entity, original.casefold())
            placeholder = assigned.get(key)
            if placeholder is None:
                counters[span.entity] = counters.get(span.entity, 0) + 1
                placeholder = f"[{span.entity.value}_{counters[span.entity]}]"
                assigned[key] = placeholder

            out.append(text[cursor : span.start])
            out.append(placeholder)
            cursor = span.end
        out.append(text[cursor:])

        return RedactionResult(
            text="".join(out), spans=tuple(spans), version=REDACTION_VERSION
        )

    def scan(self, text: str, known: KnownValues | None = None) -> tuple[Span, ...]:
        """Check text for identifiers without rewriting it.

        Used on model output before it is stored or shown. A model handed
        redacted text can still surface an identifier -- by echoing something a
        detector missed, or by reconstructing one from surrounding context --
        so the output is checked with the same detectors as the input.
        """
        return tuple(self.detect(text, known))


#: Shared default instance. Safe to reuse: recognisers hold no per-document state.
_DEFAULT = Redactor()


def redact(text: str, known: KnownValues | None = None) -> RedactionResult:
    """Convenience wrapper over the default :class:`Redactor`."""
    return _DEFAULT.redact(text, known)
