"""Tests for PII detection and redaction.

The tests that matter most here are the negative ones. A detector that flags
everything scores perfect recall and is useless: it destroys the analysis the
student came for. So alongside "does it catch the identifier", each risky rule
has a paired test asserting it does *not* fire on ordinary resume content.
"""

from __future__ import annotations

import pytest

from pps_privacy.redaction import (
    EntityType,
    KnownValues,
    RedactionError,
    Redactor,
    verhoeff_valid,
)


@pytest.fixture(scope="module")
def redactor() -> Redactor:
    return Redactor()


def valid_aadhaar(prefix: str = "2234567890") -> str:
    """Build a number that passes the Verhoeff checksum.

    Computed rather than hardcoded so the test proves the checksum logic works
    instead of just agreeing with a constant someone pasted in.
    """
    for check in "0123456789":
        candidate = prefix + "1" + check
        if verhoeff_valid(candidate):
            return candidate
    raise AssertionError("no valid check digit found")


def entities(result) -> set[EntityType]:
    return {s.entity for s in result.spans}


# --- direct identifiers -------------------------------------------------


def test_detects_email(redactor: Redactor) -> None:
    result = redactor.redact("Contact me at arjun.rao@example.edu for details.")
    assert "arjun.rao@example.edu" not in result.text
    assert EntityType.EMAIL in entities(result)


@pytest.mark.parametrize(
    "number",
    ["+91 98765 43210", "+919876543210", "9876543210", "98765-43210", "+91-98765-43210"],
)
def test_detects_indian_phone_in_any_format(redactor: Redactor, number: str) -> None:
    result = redactor.redact(f"Phone: {number}")
    assert "9876" not in result.text
    assert EntityType.PHONE in entities(result)


def test_detects_profile_urls(redactor: Redactor) -> None:
    result = redactor.redact(
        "linkedin.com/in/arjun-rao-12345 and https://github.com/arjunrao"
    )
    assert "arjun-rao" not in result.text
    assert "arjunrao" not in result.text
    assert len([s for s in result.spans if s.entity is EntityType.URL_PROFILE]) == 2


def test_does_not_flag_ordinary_urls(redactor: Redactor) -> None:
    """A company or project link is not an identifier.

    Redacting every URL would strip the portfolio evidence the analysis is
    supposed to reward.
    """
    result = redactor.redact("Built with https://react.dev and deployed on aws.amazon.com")
    assert "react.dev" in result.text
    assert "aws.amazon.com" in result.text


# --- government identifiers, and the false positives they invite --------


def test_detects_valid_aadhaar(redactor: Redactor) -> None:
    aadhaar = valid_aadhaar()
    result = redactor.redact(f"Aadhaar No: {aadhaar}")
    assert aadhaar not in result.text
    assert EntityType.AADHAAR in entities(result)


def test_ignores_twelve_digits_that_fail_the_checksum(redactor: Redactor) -> None:
    """The reason the Verhoeff check is worth implementing.

    Resumes are full of twelve-digit numbers -- order IDs, transaction
    references, phone numbers with codes. Without the checksum this rule fires
    on all of them.
    """
    assert not verhoeff_valid("123456789012")
    result = redactor.redact("Processed order 1234 5678 9012 for the client.")
    assert "1234 5678 9012" in result.text
    assert EntityType.AADHAAR not in entities(result)


def test_ignores_aadhaar_shaped_numbers_starting_with_zero(redactor: Redactor) -> None:
    result = redactor.redact("Reference 0123 4567 8901 was closed.")
    assert EntityType.AADHAAR not in entities(result)


def test_detects_pan(redactor: Redactor) -> None:
    result = redactor.redact("PAN: ABCDE1234F")
    assert "ABCDE1234F" not in result.text
    assert EntityType.PAN in entities(result)


def test_does_not_flag_lowercase_pan_shaped_text(redactor: Redactor) -> None:
    """PAN is always upper case; matching case-insensitively hits real words."""
    result = redactor.redact("The abcde1234f identifier is internal.")
    assert EntityType.PAN not in entities(result)


# --- protected characteristics ------------------------------------------


@pytest.mark.parametrize(
    ("text", "secret", "entity"),
    [
        ("Date of Birth: 1999-04-02", "1999-04-02", EntityType.DATE_OF_BIRTH),
        ("DOB: 02/04/1999", "02/04/1999", EntityType.DATE_OF_BIRTH),
        ("Gender: Female", "Female", EntityType.GENDER),
        ("Marital Status: Single", "Single", EntityType.MARITAL_STATUS),
        ("Nationality: Indian", "Indian", EntityType.NATIONALITY),
        ("Religion: Hindu", "Hindu", EntityType.RELIGION),
        ("Father's Name: Rajesh Kumar Sharma", "Rajesh Kumar Sharma", EntityType.REFEREE),
    ],
)
def test_detects_labelled_sensitive_fields(
    redactor: Redactor, text: str, secret: str, entity: EntityType
) -> None:
    result = redactor.redact(text)
    assert secret not in result.text
    assert entity in entities(result)


def test_label_survives_so_the_student_can_be_told(redactor: Redactor) -> None:
    """Only the value goes. Keeping the label lets the analysis say
    'remove the date of birth field', which it could not do if the whole line
    vanished."""
    result = redactor.redact("Date of Birth: 1999-04-02")
    assert "Date of Birth" in result.text
    assert "1999" not in result.text


def test_employment_dates_are_not_mistaken_for_a_birth_date(redactor: Redactor) -> None:
    result = redactor.redact("Software Engineer, Jan 2021 - Mar 2024")
    assert "Jan 2021" in result.text
    assert EntityType.DATE_OF_BIRTH not in entities(result)


def test_reports_prohibited_findings(redactor: Redactor) -> None:
    result = redactor.redact("DOB: 1999-04-02\nGender: Male\nPAN: ABCDE1234F")
    found = set(result.found_prohibited)
    assert {EntityType.DATE_OF_BIRTH, EntityType.GENDER, EntityType.PAN} <= found


# --- known values: the high-recall layer --------------------------------


def test_matches_name_in_all_caps(redactor: Redactor) -> None:
    """Resume headers are routinely ALL CAPS, where NER performs worst."""
    known = KnownValues(name="Priya Sharma")
    result = redactor.redact("PRIYA SHARMA\nData Analyst", known)
    assert "PRIYA SHARMA" not in result.text
    assert "Data Analyst" in result.text


def test_matches_surname_first(redactor: Redactor) -> None:
    known = KnownValues(name="Priya Sharma")
    result = redactor.redact("Sharma Priya, B.Tech", known)
    assert "Sharma Priya" not in result.text


def test_matches_email_local_part_used_as_a_handle(redactor: Redactor) -> None:
    known = KnownValues(emails=("priya.sharma@example.edu",))
    result = redactor.redact("Username: priya.sharma on the internal portal", known)
    assert "priya.sharma" not in result.text


def test_matches_phone_however_it_is_punctuated(redactor: Redactor) -> None:
    known = KnownValues(phones=("9876543210",))
    result = redactor.redact("Reach me on (98765) 43210 any time", known)
    assert "43210" not in result.text


def test_country_code_is_consumed_with_the_number(redactor: Redactor) -> None:
    """A stranded '+91' reveals the country and reads like a bug."""
    known = KnownValues(phones=("9876543210",))
    result = redactor.redact("Mobile: +91 98765 43210", known)
    assert "+91" not in result.text


def test_short_name_parts_are_not_redacted(redactor: Redactor) -> None:
    """Redacting a three-letter token across a document destroys real content.

    'Raj' would otherwise match inside 'Rajasthan', 'Raja' and plain prose.
    """
    known = KnownValues(name="Raj Kumar Iyer")
    result = redactor.redact("Worked on a project in Rajasthan for Kumar Industries", known)
    assert "Rajasthan" in result.text


# --- placeholders --------------------------------------------------------


def test_same_value_gets_the_same_placeholder(redactor: Redactor) -> None:
    """Coreference survives redaction.

    The analysis can still observe that the header address matches the one in
    the contact block, without either value being present.
    """
    result = redactor.redact("a@example.edu ... later, a@example.edu again")
    assert result.text.count("[EMAIL_1]") == 2


def test_different_values_get_different_placeholders(redactor: Redactor) -> None:
    result = redactor.redact("a@example.edu and b@example.edu")
    assert "[EMAIL_1]" in result.text
    assert "[EMAIL_2]" in result.text


def test_result_does_not_carry_the_original_values(redactor: Redactor) -> None:
    """The result object is passed around and logged. It must not be a second
    copy of the data we just removed."""
    result = redactor.redact("priya@example.edu", KnownValues(name="Priya Sharma"))
    rendered = repr(result)
    assert "priya@example.edu" not in rendered


def test_entity_counts_are_safe_to_log(redactor: Redactor) -> None:
    result = redactor.redact("a@example.edu and +91 98765 43210")
    assert result.entity_counts == {"EMAIL": 1, "PHONE": 1}


def test_version_is_recorded(redactor: Redactor) -> None:
    """Stored on every analysis row, so a later leak can be traced to a build."""
    assert redactor.redact("nothing here").version


# --- overlap resolution --------------------------------------------------


def test_known_value_wins_over_a_weaker_overlapping_match(redactor: Redactor) -> None:
    """A value we hold beats one we inferred, and spans never double-replace."""
    known = KnownValues(name="Priya Sharma", emails=("priya.sharma@example.edu",))
    result = redactor.redact("Priya Sharma <priya.sharma@example.edu>", known)
    assert "[" in result.text
    assert "]]" not in result.text
    assert "Sharma" not in result.text


def test_longer_name_span_wins_over_a_shorter_one(redactor: Redactor) -> None:
    known = KnownValues(name="Priya Sharma")
    result = redactor.redact("Priya Sharma", known)
    assert result.text == "[PERSON_1]"


# --- failure behaviour ---------------------------------------------------


def test_fails_closed_when_a_recogniser_raises() -> None:
    """A detection bug must never degrade into sending the raw text."""

    class Broken:
        name = "broken"

        def find(self, text: str):
            raise RuntimeError("boom")

    with pytest.raises(RedactionError):
        Redactor([Broken()]).redact("Priya Sharma, priya@example.edu")


def test_rejects_none(redactor: Redactor) -> None:
    with pytest.raises(RedactionError):
        redactor.redact(None)  # type: ignore[arg-type]


def test_empty_text_is_not_an_error(redactor: Redactor) -> None:
    result = redactor.redact("")
    assert result.text == ""
    assert result.spans == ()


# --- output scanning -----------------------------------------------------


def test_scan_finds_identifiers_echoed_by_a_model(redactor: Redactor) -> None:
    """A model given redacted text can still surface an identifier.

    The output gets the same detectors as the input, so a leak is caught before
    the result is stored or shown.
    """
    leaked = redactor.scan("The candidate can be reached at priya@example.edu")
    assert any(s.entity is EntityType.EMAIL for s in leaked)


def test_scan_is_clean_for_well_behaved_output(redactor: Redactor) -> None:
    assert redactor.scan("The candidate shows strong Python and SQL skills.") == ()
