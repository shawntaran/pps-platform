"""Optional statistical layer: names we do not already hold.

The deterministic layers cover the account holder and anything with a pattern.
What they cannot reach is a referee, a previous manager or a colleague named in
a project description -- third-party people whose details we hold nowhere.

This adapter is optional on purpose. Presidio and a spaCy model add hundreds of
megabytes and several seconds of startup, and the pipeline is useful without
them, so nothing here is a hard dependency. Install with::

    pip install "pps-privacy[ner]"
    python -m spacy download en_core_web_lg

Two things to keep in mind when enabling it:

* **Load the model once per worker.** Constructing this inside a request turns
  a 200ms redaction into a multi-second one. It is the single biggest latency
  trap in the pipeline.
* **It runs in our infrastructure.** That is the whole point of choosing
  Presidio over a hosted PII service: detecting personal data must not itself
  require sending personal data to a third party.

Recall on resumes is the weak spot -- ALL-CAPS headers, table cells and
multi-column layouts give a model very little sentence structure to work with.
Treat its output as a supplement to the deterministic layers, and measure it
with the eval harness rather than trusting it.
"""

from __future__ import annotations

from collections.abc import Iterator

from .entities import EntityType, Span

__all__ = ["SpacyNerRecognizer", "NerUnavailable"]

# spaCy labels we map onto our own types. Everything else is ignored: dates and
# numbers are handled far more precisely by the pattern layer, and accepting
# them here would shred every employment date in the document.
_LABEL_MAP = {
    "PERSON": EntityType.PERSON,
    "GPE": EntityType.ADDRESS,
    "LOC": EntityType.ADDRESS,
    "FAC": EntityType.ADDRESS,
    "ORG": EntityType.EMPLOYER,
}


class NerUnavailable(RuntimeError):
    """spaCy or the requested model is not installed."""


class SpacyNerRecognizer:
    """Wraps a loaded spaCy pipeline as a :class:`~.recognizers.Recognizer`."""

    name = "spacy_ner"

    def __init__(self, model: str = "en_core_web_lg", *, confidence: float = 0.6) -> None:
        try:
            import spacy
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise NerUnavailable(
                "spaCy is not installed; install the 'ner' extra to enable this layer"
            ) from exc

        try:
            # Loaded here, at construction, so the cost lands at worker startup.
            self._nlp = spacy.load(model, disable=["lemmatizer", "textcat"])
        except OSError as exc:  # pragma: no cover - depends on downloaded models
            raise NerUnavailable(
                f"spaCy model {model!r} is not downloaded: python -m spacy download {model}"
            ) from exc

        # Below 1.0 because this layer infers rather than knows. Overlap
        # resolution therefore prefers a known-value or pattern match covering
        # the same text, which is the behaviour we want.
        self._confidence = confidence

    def find(self, text: str) -> Iterator[Span]:
        for ent in self._nlp(text).ents:
            entity = _LABEL_MAP.get(ent.label_)
            if entity is not None and ent.end_char > ent.start_char:
                yield Span(ent.start_char, ent.end_char, entity, self._confidence, self.name)
