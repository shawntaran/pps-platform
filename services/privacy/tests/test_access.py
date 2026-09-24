"""Tests for the authentication handover.

Two halves:

* Principal construction, which is where the boundary rule is enforced --
  a Principal may only come from verified authentication.
* End-to-end scoping against a real database, which is the proof that the
  handover actually works: hand in a Principal, get back a session that can
  only see the right rows, with no WHERE clause written by the caller.
"""

from __future__ import annotations

import os
import uuid

import pytest

from pps_privacy.access import (
    Principal,
    PrincipalError,
    Role,
    Scope,
    resolve_scope,
    scoped_session,
)

needs_db = pytest.mark.skipif(
    os.environ.get("PPS_TEST_DATABASE_URL") is None,
    reason="PPS_TEST_DATABASE_URL is not set; see tests/conftest.py",
)


# --- the boundary rule ---------------------------------------------------


def test_builds_from_verified_auth() -> None:
    uid = uuid.uuid4()
    principal = Principal.from_verified_auth(str(uid), "trainer")
    assert principal.user_id == uid
    assert principal.role is Role.TRAINER


@pytest.mark.parametrize("claimed", ["system", "SYSTEM", " System "])
def test_system_role_is_unreachable_from_a_request(claimed: str) -> None:
    """The most important test in this file.

    ``system`` is the one role whose RLS policy sees every row. If a token, a
    header or a misconfigured identity provider could ever produce it, the
    entire scoping scheme is off. So the request-path constructor refuses it
    outright, whatever casing or padding it arrives with.
    """
    with pytest.raises(PrincipalError, match="never be reachable"):
        Principal.from_verified_auth(uuid.uuid4(), claimed)


def test_system_principal_exists_for_background_workers() -> None:
    principal = Principal.system()
    assert principal.is_system
    assert principal.user_id is None


def test_unknown_role_is_rejected() -> None:
    with pytest.raises(PrincipalError, match="unknown role"):
        Principal.from_verified_auth(uuid.uuid4(), "superuser")


@pytest.mark.parametrize("bad_id", ["trn_007", "stu_014", "", "not-a-uuid", "1"])
def test_guessable_identifiers_are_rejected(bad_id: str) -> None:
    """Identifiers must be UUIDs.

    Sequential, guessable IDs turn any weakness in authentication into
    impersonation of a *chosen* person rather than a random one. Rejecting them
    here means the demo-style identifiers cannot quietly become production ones.
    """
    with pytest.raises(PrincipalError, match="UUID"):
        Principal.from_verified_auth(bad_id, "trainer")


def test_human_role_requires_a_user_id() -> None:
    with pytest.raises(PrincipalError, match="requires a user_id"):
        Principal(user_id=None, role=Role.TRAINER)


def test_system_principal_must_not_carry_a_user_id() -> None:
    with pytest.raises(PrincipalError, match="no user_id"):
        Principal(user_id=uuid.uuid4(), role=Role.SYSTEM)


def test_repr_is_short_enough_for_logs() -> None:
    principal = Principal.from_verified_auth(uuid.uuid4(), "student")
    assert "student" in repr(principal)


def test_roles_match_the_database_constraint() -> None:
    """If these drift, inserts fail at runtime instead of here."""
    from pps_privacy.access.principal import HUMAN_ROLES

    assert {r.value for r in HUMAN_ROLES} == {
        "student",
        "trainer",
        "recruiter",
        "admin",
        "dpo",
    }


# --- end-to-end scoping --------------------------------------------------


@needs_db
def test_scoped_session_limits_a_student_to_their_own_row(connect_as, seeded) -> None:
    """The caller writes no WHERE clause and still cannot see anyone else."""
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["students"][0], "student")
    scope = resolve_scope(conn, principal)

    with scoped_session(conn, principal, scope) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    assert {r[0] for r in rows} == {seeded["students"][0]}


@needs_db
def test_scoped_session_gives_a_trainer_their_batch(connect_as, seeded) -> None:
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["trainer"], "trainer")
    scope = resolve_scope(conn, principal)

    with scoped_session(conn, principal, scope) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    visible = {r[0] for r in rows}
    assert set(seeded["students"]) <= visible
    assert seeded["outsider"] not in visible


@needs_db
def test_resolve_scope_finds_active_assignments_only(connect_as, seeded) -> None:
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["trainer"], "trainer")

    assert resolve_scope(conn, principal).trainer_batches == (seeded["batch"],)

    conn.execute("SET app.actor_role = 'system'")
    conn.execute(
        "UPDATE identity.trainer_assignments SET revoked_at = now() WHERE trainer_id = %s",
        (seeded["trainer"],),
    )
    assert resolve_scope(conn, principal).trainer_batches == ()


@needs_db
def test_unassigned_trainer_is_scoped_to_nothing(connect_as, seeded) -> None:
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["unassigned_trainer"], "trainer")
    scope = resolve_scope(conn, principal)

    with scoped_session(conn, principal, scope) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    assert {r[0] for r in rows} == {seeded["unassigned_trainer"]}


@needs_db
def test_identity_scope_is_derived_by_the_database(connect_as, seeded) -> None:
    """Inside the identity zone, scoping does not depend on the caller.

    The policy checks ``trainer_assignments`` itself, so a trainer sees their
    batch even when the caller passes an empty Scope. That is the more robust
    half of a deliberate asymmetry: forgetting to resolve scope cannot silently
    widen access here, because the database is not taking the caller's word for
    it. The analysis zone cannot do this -- see the next test.
    """
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["trainer"], "trainer")

    with scoped_session(conn, principal, Scope()) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    assert set(seeded["students"]) <= {r[0] for r in rows}


@needs_db
def test_analysis_scope_fails_closed_without_resolved_batches(connect_as, seeded) -> None:
    """In the analysis zone, scoping *does* depend on the caller, and an
    unresolved scope must lose access rather than grant it.

    This zone has no route to the identity schema by design, so it cannot check
    batch membership itself and relies on ``app.trainer_batches`` instead.
    """
    writer = connect_as("t_analysis")
    writer.execute("SET app.actor_role = 'system'")
    writer.execute(
        "INSERT INTO analysis.analyses (candidate_pid, resume_pid, batch_id, model_id, "
        "model_version, prompt_version, redaction_version, expires_at) "
        "VALUES (%s, %s, %s, 'claude-opus-5', 'v1', 'p1', '1.0.0', now() + interval '1 year')",
        (seeded["student_pids"][0], uuid.uuid4(), seeded["batch"]),
    )

    conn = connect_as("t_analysis")
    principal = Principal.from_verified_auth(seeded["trainer"], "trainer")

    with scoped_session(conn, principal, Scope()) as session:
        blind = session.execute("SELECT count(*) FROM analysis.analyses").fetchone()[0]
    assert blind == 0

    with scoped_session(
        conn, principal, Scope(trainer_batches=(seeded["batch"],))
    ) as session:
        scoped = session.execute("SELECT count(*) FROM analysis.analyses").fetchone()[0]
    assert scoped >= 1


@needs_db
@pytest.mark.parametrize("login", ["t_identity", "t_analysis", "t_compliance", "t_auth"])
def test_session_helpers_are_callable_by_every_role(connect_as, login: str) -> None:
    """Regression guard for a trap that nearly shipped.

    These helpers originally lived in the identity schema, which the analysis
    role cannot use. The policies still worked -- but only because PostgreSQL
    inlines simple SQL functions and erases the schema reference before
    checking permissions. Rewriting either helper as PL/pgSQL would have
    stopped the inlining and broken every analysis-zone query in production,
    with an error pointing at schema permissions rather than at the edit.

    Calling them directly is what distinguishes "every role may use these" from
    "the planner happens to optimise the problem away".
    """
    conn = connect_as(login)
    assert conn.execute("SELECT app_context.actor_role()").fetchone()[0] == "anonymous"
    assert conn.execute("SELECT app_context.actor_id()").fetchone()[0] is None


@needs_db
def test_context_does_not_outlive_the_transaction(connect_as, seeded) -> None:
    """Connections are pooled, so a leaked setting would hand one user's scope
    to whoever borrows the connection next. This is the bug that would matter
    most, so it gets its own test."""
    conn = connect_as("t_identity")
    principal = Principal.from_verified_auth(seeded["students"][0], "student")

    with scoped_session(conn, principal, resolve_scope(conn, principal)):
        pass

    leftover = conn.execute("SELECT current_setting('app.actor_id', true)").fetchone()[0]
    assert not leftover

    # And the connection is back to seeing nothing without a fresh context.
    rows = conn.execute("SELECT user_id FROM identity.users").fetchall()
    assert rows == []


@needs_db
def test_system_principal_sees_everything(connect_as, seeded) -> None:
    """Background workers need full visibility; this is what the retention
    sweep and the deletion worker run as."""
    conn = connect_as("t_identity")

    with scoped_session(conn, Principal.system()) as session:
        rows = session.execute("SELECT user_id FROM identity.users").fetchall()

    assert len(rows) >= 5
