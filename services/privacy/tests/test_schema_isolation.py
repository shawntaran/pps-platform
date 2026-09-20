"""Integration tests: does the database actually enforce the access matrix?

Every test here connects as a real service role. Running as the table owner
would prove nothing, because the owner can do everything.

Skipped unless PPS_TEST_DATABASE_URL is set -- see conftest.py.
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import pytest

# Defined here rather than imported from conftest: pytest does not put the
# tests directory on sys.path, so a relative import fails at collection.
pytestmark = pytest.mark.skipif(
    os.environ.get("PPS_TEST_DATABASE_URL") is None,
    reason="PPS_TEST_DATABASE_URL is not set; see tests/conftest.py",
)


def _blob() -> bytes:
    """Stand-in ciphertext. These tests are about access, not cryptography."""
    return os.urandom(48)


@pytest.fixture
def seeded(connect_as) -> dict[str, Any]:
    """One batch, two students, two trainers -- only one of them assigned.

    The second trainer is the control: if they can see the students, the batch
    scope is not doing anything.
    """
    conn = connect_as("t_identity")
    conn.execute("SET app.actor_role = 'system'")

    batch = conn.execute(
        "INSERT INTO identity.batches (name, programme, institution, graduation_date) "
        "VALUES ('B1', 'CS', 'Example University', '2027-06-30') RETURNING batch_id"
    ).fetchone()[0]
    other_batch = conn.execute(
        "INSERT INTO identity.batches (name, programme, institution, graduation_date) "
        "VALUES ('B2', 'CS', 'Example University', '2027-06-30') RETURNING batch_id"
    ).fetchone()[0]

    def add_user(role: str) -> uuid.UUID:
        return conn.execute(
            "INSERT INTO identity.users (role, name_enc, wrapped_dek) "
            "VALUES (%s, %s, %s) RETURNING user_id",
            (role, _blob(), _blob()),
        ).fetchone()[0]

    students = [add_user("student") for _ in range(2)]
    trainer = add_user("trainer")
    unassigned_trainer = add_user("trainer")
    outsider = add_user("student")

    for student in students:
        conn.execute(
            "INSERT INTO identity.batch_enrollments (user_id, batch_id) VALUES (%s, %s)",
            (student, batch),
        )
    conn.execute(
        "INSERT INTO identity.batch_enrollments (user_id, batch_id) VALUES (%s, %s)",
        (outsider, other_batch),
    )
    conn.execute(
        "INSERT INTO identity.trainer_assignments (trainer_id, batch_id) VALUES (%s, %s)",
        (trainer, batch),
    )

    return {
        "batch": batch,
        "other_batch": other_batch,
        "students": students,
        "trainer": trainer,
        "unassigned_trainer": unassigned_trainer,
        "outsider": outsider,
    }


def _as(conn, actor_id, role: str):
    conn.execute(f"SET app.actor_role = '{role}'")
    conn.execute(f"SET app.actor_id = '{actor_id}'")
    return conn


# --- zone separation ----------------------------------------------------


def test_analysis_role_cannot_reach_identity(connect_as, psycopg) -> None:
    """The load-bearing test for the whole zone design.

    The analysis service has no USAGE on the identity schema, so a careless
    join or an injected query fails with a permission error rather than
    returning a student. If this test ever fails, the separation is gone and
    everything built on it is a claim we can no longer make.
    """
    conn = connect_as("t_analysis")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT * FROM identity.users")


def test_analysis_role_cannot_reach_compliance(connect_as, psycopg) -> None:
    conn = connect_as("t_analysis")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT * FROM compliance.consent_records")


def test_identity_role_cannot_read_credentials(connect_as, psycopg) -> None:
    """Password hashes are reachable by the auth role alone.

    Not admin, not the DPO, not the service that serves the application.
    """
    conn = connect_as("t_identity")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT password_hash FROM identity.credentials")


def test_auth_role_cannot_read_user_identities(connect_as, psycopg) -> None:
    """Authentication never needs a student name, so it cannot have one."""
    conn = connect_as("t_auth")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT name_enc FROM identity.users")


def test_analysis_tables_have_no_foreign_keys_into_identity(connect_as) -> None:
    """A cross-zone FK would force the analysis role to reach identity.

    This asserts the absence is deliberate, so a future migration that adds
    "just one" reference fails here and has to justify itself.
    """
    conn = connect_as("t_identity")
    rows = conn.execute(
        """
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class child ON child.oid = con.conrelid
        JOIN pg_namespace child_ns ON child_ns.oid = child.relnamespace
        JOIN pg_class parent ON parent.oid = con.confrelid
        JOIN pg_namespace parent_ns ON parent_ns.oid = parent.relnamespace
        WHERE con.contype = 'f'
          AND child_ns.nspname = 'analysis'
          AND parent_ns.nspname = 'identity'
        """
    ).fetchall()
    assert rows == []


# --- row-level security: batch scoping ----------------------------------


def test_student_sees_only_their_own_row(connect_as, seeded) -> None:
    conn = _as(connect_as("t_identity"), seeded["students"][0], "student")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    assert visible == {seeded["students"][0]}


def test_trainer_sees_their_batch(connect_as, seeded) -> None:
    conn = _as(connect_as("t_identity"), seeded["trainer"], "trainer")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    # Their assigned students, plus their own row via the self policy.
    assert set(seeded["students"]).issubset(visible)
    assert seeded["trainer"] in visible


def test_trainer_cannot_see_other_batches(connect_as, seeded) -> None:
    conn = _as(connect_as("t_identity"), seeded["trainer"], "trainer")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    assert seeded["outsider"] not in visible


def test_unassigned_trainer_sees_no_students(connect_as, seeded) -> None:
    """The control case. Being a trainer is not itself access to anything."""
    conn = _as(connect_as("t_identity"), seeded["unassigned_trainer"], "trainer")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    assert visible == {seeded["unassigned_trainer"]}


def test_revoked_assignment_ends_access(connect_as, seeded) -> None:
    """Access ends when the teaching does, including for former batches."""
    admin = connect_as("t_identity")
    admin.execute("SET app.actor_role = 'system'")
    admin.execute(
        "UPDATE identity.trainer_assignments SET revoked_at = now() "
        "WHERE trainer_id = %s AND batch_id = %s",
        (seeded["trainer"], seeded["batch"]),
    )

    conn = _as(connect_as("t_identity"), seeded["trainer"], "trainer")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    assert not set(seeded["students"]) & visible


def test_programme_toggle_off_hides_identities(connect_as, seeded) -> None:
    """trainer_identity_access = false puts a programme in pseudonymous mode."""
    admin = connect_as("t_identity")
    admin.execute("SET app.actor_role = 'system'")
    admin.execute(
        "UPDATE identity.batches SET trainer_identity_access = false WHERE batch_id = %s",
        (seeded["batch"],),
    )

    conn = _as(connect_as("t_identity"), seeded["trainer"], "trainer")
    visible = {r[0] for r in conn.execute("SELECT user_id FROM identity.users").fetchall()}
    assert not set(seeded["students"]) & visible


def test_anonymous_session_sees_nothing(connect_as, seeded) -> None:
    """An unset session context must fail closed, not open."""
    conn = connect_as("t_identity")
    rows = conn.execute("SELECT user_id FROM identity.users").fetchall()
    assert rows == []


# --- the trainer field allowlist ----------------------------------------


def test_trainer_view_omits_personal_contact_fields(connect_as, seeded) -> None:
    """The allowlist is the view's column list, not a filter in app code.

    Personal email and phone are absent from the relation entirely, so there is
    no query a trainer can write that returns them.
    """
    conn = connect_as("t_identity")
    columns = {
        r[0]
        for r in conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'identity' AND table_name = 'trainer_student_view'"
        ).fetchall()
    }
    assert {"name_enc", "student_ref_enc", "inst_email_enc"} <= columns
    assert "personal_email_enc" not in columns
    assert "phone_enc" not in columns
    assert "graduation_date_override" not in columns


def test_trainer_view_still_applies_batch_scope(connect_as, seeded) -> None:
    """security_invoker: the view must not bypass the RLS policies.

    A view defined without it runs as its owner and would hand every student to
    every trainer -- worse than having no view at all.
    """
    conn = _as(connect_as("t_identity"), seeded["unassigned_trainer"], "trainer")
    rows = conn.execute("SELECT user_id FROM identity.trainer_student_view").fetchall()
    assert rows == []


# --- append-only compliance records -------------------------------------


@pytest.fixture
def consent_row(connect_as, seeded) -> uuid.UUID:
    conn = connect_as("t_compliance")
    conn.execute(
        "INSERT INTO compliance.policy_versions (version, text_hash) "
        "VALUES ('v1.0', %s) ON CONFLICT DO NOTHING",
        (_blob(),),
    )
    return conn.execute(
        "INSERT INTO compliance.consent_records "
        "(subject_pid, purpose_code, action, policy_version, notice_hash) "
        "VALUES (%s, 'resume_analysis', 'granted', 'v1.0', %s) RETURNING consent_id",
        (uuid.uuid4(), _blob()),
    ).fetchone()[0]


def test_consent_records_cannot_be_updated(connect_as, consent_row, psycopg) -> None:
    """Proof of consent is worth nothing if the record can be edited later."""
    conn = connect_as("t_compliance")
    with pytest.raises((psycopg.errors.InsufficientPrivilege, psycopg.errors.RaiseException)):
        conn.execute(
            "UPDATE compliance.consent_records SET action = 'withdrawn' WHERE consent_id = %s",
            (consent_row,),
        )


def test_consent_records_cannot_be_deleted(connect_as, consent_row, psycopg) -> None:
    conn = connect_as("t_compliance")
    with pytest.raises((psycopg.errors.InsufficientPrivilege, psycopg.errors.RaiseException)):
        conn.execute(
            "DELETE FROM compliance.consent_records WHERE consent_id = %s", (consent_row,)
        )


def test_withdrawal_is_a_new_row(connect_as, consent_row) -> None:
    """The intended path: state is the latest row, history stays intact."""
    conn = connect_as("t_compliance")
    subject = conn.execute(
        "SELECT subject_pid FROM compliance.consent_records WHERE consent_id = %s",
        (consent_row,),
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO compliance.consent_records "
        "(subject_pid, purpose_code, action, policy_version, notice_hash) "
        "VALUES (%s, 'resume_analysis', 'withdrawn', 'v1.0', %s)",
        (subject, _blob()),
    )
    rows = conn.execute(
        "SELECT action FROM compliance.consent_records "
        "WHERE subject_pid = %s ORDER BY occurred_at",
        (subject,),
    ).fetchall()
    assert [r[0] for r in rows] == ["granted", "withdrawn"]


def test_audit_log_cannot_be_rewritten(connect_as, psycopg) -> None:
    conn = connect_as("t_compliance")
    event = conn.execute(
        "INSERT INTO compliance.audit_log (actor_role, action) "
        "VALUES ('trainer', 'view_identity') RETURNING event_id"
    ).fetchone()[0]
    with pytest.raises((psycopg.errors.InsufficientPrivilege, psycopg.errors.RaiseException)):
        conn.execute("DELETE FROM compliance.audit_log WHERE event_id = %s", (event,))
