"""Redaction eval: a measured recall gate, not a vibe check.

The residency argument in docs/privacy/infra-residency-and-latency.md depends
on redaction working. "It looked fine when I tried it" is not a basis for
telling a student their personal details were removed before their resume
reached a third party, so this file measures it and fails the build when recall
drops.

**Metric.** For each document we assert on the thing that actually matters: did
a given identifier survive into the output? Not "did we emit a span" -- a span
at the wrong offset still leaks. The check is substring absence from the final
redacted text.

**Two thresholds, because both failure modes are real.**

* *Recall* on direct identifiers must be 100% here. Anything less means a name,
  an address or a government ID reached the model.
* *Preservation* must also be 100%. A detector that redacts everything scores
  perfect recall and destroys the analysis the student came for, so the corpus
  asserts that legitimate content survives.

**What this is not.** Passing is a regression gate on a small hand-built
corpus, not evidence of real-world recall. Before launch this needs a larger
generated corpus over real resume layouts -- multi-column PDFs, tables, scanned
documents -- with per-entity numbers tracked over time. Treat 100% here as "no
known regressions", never as "redaction is solved".

All names, addresses and numbers below are invented. No real student data ever
belongs in a test fixture.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from pps_privacy.redaction import EntityType, KnownValues, Redactor


@dataclass(frozen=True)
class Case:
    """One synthetic resume and what must and must not survive redaction."""

    name: str
    text: str
    known: KnownValues
    #: Substrings that must be gone, grouped by the type they represent.
    must_remove: dict[EntityType, tuple[str, ...]]
    #: Legitimate content that must still be present afterwards.
    must_keep: tuple[str, ...] = field(default=())


CASES: tuple[Case, ...] = (
    Case(
        name="conventional_layout",
        text=(
            "Priya Sharma\n"
            "Bengaluru, Karnataka | priya.sharma@example.edu | +91 98765 43210\n"
            "linkedin.com/in/priya-sharma-dev\n\n"
            "SUMMARY\n"
            "Data analyst with three years of experience in Python and SQL.\n\n"
            "EXPERIENCE\n"
            "Data Analyst, Contoso Analytics, Jan 2022 - Present\n"
            "Built ETL pipelines processing 2M records daily.\n"
        ),
        known=KnownValues(
            name="Priya Sharma",
            emails=("priya.sharma@example.edu",),
            phones=("9876543210",),
        ),
        must_remove={
            EntityType.PERSON: ("Priya Sharma",),
            EntityType.EMAIL: ("priya.sharma@example.edu",),
            EntityType.PHONE: ("98765 43210",),
            EntityType.URL_PROFILE: ("priya-sharma-dev",),
        },
        must_keep=("Python and SQL", "ETL pipelines", "Data Analyst"),
    ),
    Case(
        name="all_caps_header",
        # ALL CAPS with no sentence structure is where statistical name
        # detection performs worst, and where the known-value layer earns its
        # place.
        text=(
            "ARJUN RAO\n"
            "ARJUN.RAO@EXAMPLE.EDU | 9123456780\n\n"
            "OBJECTIVE\n"
            "Seeking a backend engineering role.\n"
        ),
        known=KnownValues(
            name="Arjun Rao", emails=("arjun.rao@example.edu",), phones=("9123456780",)
        ),
        must_remove={
            EntityType.PERSON: ("ARJUN RAO",),
            EntityType.EMAIL: ("ARJUN.RAO@EXAMPLE.EDU",),
            EntityType.PHONE: ("9123456780",),
        },
        must_keep=("backend engineering",),
    ),
    Case(
        name="indian_template_with_personal_details",
        # This block is standard on many Indian resume templates. Every field
        # in it is a protected characteristic or third-party data.
        text=(
            "Name: Kavya Nair\n"
            "Date of Birth: 12/08/2001\n"
            "Gender: Female\n"
            "Marital Status: Single\n"
            "Nationality: Indian\n"
            "Father's Name: Suresh Nair\n"
            "Roll No: PPS-2024-4027\n\n"
            "SKILLS\n"
            "Java, Spring Boot, PostgreSQL\n"
        ),
        known=KnownValues(name="Kavya Nair", student_ref="PPS-2024-4027"),
        must_remove={
            EntityType.PERSON: ("Kavya Nair",),
            EntityType.DATE_OF_BIRTH: ("12/08/2001",),
            EntityType.GENDER: ("Female",),
            EntityType.MARITAL_STATUS: ("Single",),
            EntityType.NATIONALITY: ("Indian",),
            EntityType.REFEREE: ("Suresh Nair",),
            EntityType.STUDENT_REF: ("PPS-2024-4027",),
        },
        must_keep=("Java", "Spring Boot", "PostgreSQL"),
    ),
    Case(
        name="government_identifiers",
        text=(
            "Rohan Desai\n"
            "PAN: ABCDE1234F\n"
            # Checksum-valid (invented) Aadhaar. It has to pass Verhoeff or the
            # detector correctly ignores it and the case proves nothing.
            "Aadhaar: 2234 5678 9018\n"
            "Passport: K1234567\n\n"
            "Certified AWS Solutions Architect.\n"
        ),
        known=KnownValues(name="Rohan Desai"),
        must_remove={
            EntityType.PERSON: ("Rohan Desai",),
            EntityType.PAN: ("ABCDE1234F",),
            EntityType.AADHAAR: ("2234 5678 9018",),
            EntityType.PASSPORT: ("K1234567",),
        },
        must_keep=("AWS Solutions Architect",),
    ),
    Case(
        name="surname_first_and_repeated_contact",
        text=(
            "Iyer Meenakshi\n"
            "Email: meenakshi.iyer@example.edu\n"
            "Alternate: meenakshi.iyer@example.edu\n"
            "Mobile: (98200) 12345\n\n"
            "Led a team of six engineers at Fabrikam.\n"
        ),
        known=KnownValues(
            name="Meenakshi Iyer",
            emails=("meenakshi.iyer@example.edu",),
            phones=("9820012345",),
        ),
        must_remove={
            EntityType.PERSON: ("Iyer Meenakshi",),
            EntityType.EMAIL: ("meenakshi.iyer@example.edu",),
            EntityType.PHONE: ("12345",),
        },
        must_keep=("team of six engineers",),
    ),
    Case(
        name="profile_links_and_ordinary_links",
        # The distinction matters: a handle is an identifier, a tech link is
        # evidence the analysis should reward.
        text=(
            "Sanjay Verma\n"
            "github.com/sanjayverma | https://linkedin.com/in/sanjay-verma-99\n"
            "Portfolio built with https://nextjs.org and hosted on vercel.com\n"
        ),
        known=KnownValues(name="Sanjay Verma"),
        must_remove={
            EntityType.PERSON: ("Sanjay Verma",),
            EntityType.URL_PROFILE: ("github.com/sanjayverma", "sanjay-verma-99"),
        },
        must_keep=("nextjs.org", "vercel.com"),
    ),
    Case(
        name="noisy_numbers_that_must_survive",
        # The false-positive control. A resume is full of numbers, and a
        # detector that eats them produces a useless analysis.
        text=(
            "Ananya Krishnan\n"
            "Processed order 1234 5678 9012 for a client.\n"
            "Improved throughput by 35% across 12 services.\n"
            "Employment: Mar 2019 - Aug 2023.\n"
            "Handled budgets of 4500000 INR.\n"
        ),
        known=KnownValues(name="Ananya Krishnan"),
        must_remove={EntityType.PERSON: ("Ananya Krishnan",)},
        must_keep=(
            "1234 5678 9012",
            "35%",
            "12 services",
            "Mar 2019 - Aug 2023",
            "4500000",
        ),
    ),
)


@pytest.fixture(scope="module")
def redactor() -> Redactor:
    return Redactor()


@pytest.fixture(scope="module")
def outcomes(redactor: Redactor) -> dict[str, dict]:
    """Redact every case once and collect what survived."""
    results = {}
    for case in CASES:
        redacted = redactor.redact(case.text, case.known).text
        leaked = {
            entity: tuple(v for v in values if v in redacted)
            for entity, values in case.must_remove.items()
        }
        results[case.name] = {
            "case": case,
            "redacted": redacted,
            "leaked": {e: v for e, v in leaked.items() if v},
            "destroyed": tuple(v for v in case.must_keep if v not in redacted),
        }
    return results


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_no_identifier_survives(case: Case, outcomes: dict[str, dict]) -> None:
    """Recall, measured on the output rather than on span bookkeeping."""
    leaked = outcomes[case.name]["leaked"]
    assert not leaked, (
        f"{case.name}: identifiers survived redaction: "
        + "; ".join(f"{e.value}={v}" for e, v in leaked.items())
        + f"\n--- redacted output ---\n{outcomes[case.name]['redacted']}"
    )


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_legitimate_content_survives(case: Case, outcomes: dict[str, dict]) -> None:
    """Over-redaction is a real failure, not a safe default.

    Destroying skills, metrics and dates produces a confident, useless
    analysis -- and trains reviewers to ignore the warnings.
    """
    destroyed = outcomes[case.name]["destroyed"]
    assert not destroyed, (
        f"{case.name}: over-redacted legitimate content: {destroyed}"
        f"\n--- redacted output ---\n{outcomes[case.name]['redacted']}"
    )


def test_corpus_recall_by_entity_type(outcomes: dict[str, dict]) -> None:
    """Aggregate recall per entity type, with the numbers printed.

    Run with ``-s`` to see the table. It is the number to quote when the lead
    or a reviewer asks how well redaction actually works -- and the number to
    watch when the detectors change.
    """
    totals: dict[EntityType, list[int]] = {}
    for record in outcomes.values():
        case: Case = record["case"]
        for entity, values in case.must_remove.items():
            hit, total = totals.setdefault(entity, [0, 0])
            leaked = record["leaked"].get(entity, ())
            totals[entity] = [hit + len(values) - len(leaked), total + len(values)]

    print("\n  entity                recall")
    print("  " + "-" * 34)
    failures = []
    for entity in sorted(totals, key=lambda e: e.value):
        caught, total = totals[entity]
        recall = caught / total
        print(f"  {entity.value:<20}  {caught}/{total}  {recall:6.1%}")
        if recall < 1.0:
            failures.append(f"{entity.value} {recall:.1%}")

    assert not failures, f"recall below the gate: {', '.join(failures)}"


def test_gate_has_meaningful_coverage() -> None:
    """Guards the guard.

    A shrinking corpus would quietly weaken the gate while still reporting
    100%, so assert the eval keeps covering the identifier types we claim to
    remove.
    """
    covered = {e for case in CASES for e in case.must_remove}
    required = {
        EntityType.PERSON,
        EntityType.EMAIL,
        EntityType.PHONE,
        EntityType.URL_PROFILE,
        EntityType.DATE_OF_BIRTH,
        EntityType.GENDER,
        EntityType.STUDENT_REF,
        # The highest-sensitivity identifier in this context. An earlier draft
        # of this corpus carried a malformed Aadhaar that no rule could match
        # and asserted nothing about it, so the gate reported full coverage
        # while testing nothing.
        EntityType.AADHAAR,
    }
    assert required <= covered, f"eval no longer covers: {required - covered}"
    assert len(CASES) >= 6
