"""Shared fixtures.

Database tests are skipped unless ``PPS_TEST_DATABASE_URL`` points at a
throwaway PostgreSQL 15+ instance. Start one with::

    docker compose -f services/privacy/docker-compose.dev.yml up -d
    export PPS_TEST_DATABASE_URL=postgresql://pps:pps@localhost:5433/pps_test

Never point this at anything real: the fixture drops and recreates the schemas
on every run.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parent.parent

# Login roles used to prove the grants actually bite. Each is granted into one
# service role, so a test can connect *as* the analysis service and be refused.
TEST_LOGINS = {
    "t_identity": "pps_identity",
    "t_analysis": "pps_analysis",
    "t_compliance": "pps_compliance",
    "t_auth": "pps_auth",
}
TEST_PASSWORD = "test-only-not-a-secret"


def _url() -> str | None:
    return os.environ.get("PPS_TEST_DATABASE_URL")


def _drop_login(conn, login: str) -> None:
    """Remove a test login role and everything that depends on it.

    A plain DROP ROLE fails while the role still holds privileges -- CONNECT on
    the database is enough. DROP OWNED BY revokes those first, and both
    statements are guarded so this works whether or not the role exists.
    """
    conn.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{login}') THEN
                EXECUTE 'DROP OWNED BY {login}';
                EXECUTE 'DROP ROLE {login}';
            END IF;
        END
        $$
        """
    )


requires_db = pytest.mark.skipif(
    _url() is None,
    reason="PPS_TEST_DATABASE_URL is not set; see tests/conftest.py",
)


@pytest.fixture(scope="session")
def psycopg():
    return pytest.importorskip("psycopg")


@pytest.fixture(scope="session")
def migrated_db(psycopg) -> Iterator[str]:
    """Apply every migration to a clean database, then hand back its URL."""
    url = _url()
    if url is None:  # pragma: no cover - guarded by requires_db
        pytest.skip("PPS_TEST_DATABASE_URL is not set")

    with psycopg.connect(url, autocommit=True) as conn:
        version = conn.execute("SHOW server_version_num").fetchone()[0]
        if int(version) < 150000:
            pytest.skip(f"needs PostgreSQL 15+ for security_invoker views, got {version}")

        # Clean slate. Safe only because this must be a throwaway database.
        #
        # Discovered rather than hardcoded: an earlier version listed the three
        # schemas by name, so when a migration added a fourth the reset silently
        # stopped being a reset and the next run failed on an object that was
        # never dropped. Anything a migration creates gets cleaned up here
        # without this fixture having to know about it.
        schemas = [
            r[0]
            for r in conn.execute(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name NOT IN ('public', 'information_schema') "
                "AND schema_name NOT LIKE 'pg\\_%'"
            ).fetchall()
        ]
        for schema in schemas:
            conn.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        conn.execute("DROP TABLE IF EXISTS alembic_version")

    # Alembic wants the SQLAlchemy-style driver prefix.
    alembic_url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=SERVICE_ROOT,
        env={**os.environ, "DATABASE_URL": alembic_url},
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"migrations failed:\n{result.stdout}\n{result.stderr}")

    with psycopg.connect(url, autocommit=True) as conn:
        for login, service_role in TEST_LOGINS.items():
            _drop_login(conn, login)
            conn.execute(f"CREATE ROLE {login} LOGIN PASSWORD '{TEST_PASSWORD}'")
            conn.execute(f"GRANT {service_role} TO {login}")
            conn.execute(f"GRANT CONNECT ON DATABASE {conn.info.dbname} TO {login}")

    yield url

    with psycopg.connect(url, autocommit=True) as conn:
        for login in TEST_LOGINS:
            _drop_login(conn, login)


def blob() -> bytes:
    """Stand-in ciphertext for tests that are about access, not cryptography."""
    return os.urandom(48)


@pytest.fixture
def seeded(connect_as) -> dict:
    """One batch, two students, two trainers -- only one of them assigned.

    The unassigned trainer is the control: if they can see the students, batch
    scoping is not doing anything and the test proves nothing.

    Shared between the raw-SQL schema tests and the access-layer tests, so both
    assert against the same shape of data.
    """
    conn = connect_as("t_identity")
    conn.execute("SET app.actor_role = 'system'")

    def add_batch(name: str):
        return conn.execute(
            "INSERT INTO identity.batches (name, programme, institution, graduation_date) "
            "VALUES (%s, 'CS', 'Example University', '2027-06-30') RETURNING batch_id",
            (name,),
        ).fetchone()[0]

    def add_user(role: str):
        return conn.execute(
            "INSERT INTO identity.users (role, name_enc, wrapped_dek) "
            "VALUES (%s, %s, %s) RETURNING user_id, candidate_pid",
            (role, blob(), blob()),
        ).fetchone()

    batch = add_batch("B1")
    other_batch = add_batch("B2")

    student_rows = [add_user("student") for _ in range(2)]
    trainer_row = add_user("trainer")
    unassigned_row = add_user("trainer")
    outsider_row = add_user("student")

    for user_id, _ in student_rows:
        conn.execute(
            "INSERT INTO identity.batch_enrollments (user_id, batch_id) VALUES (%s, %s)",
            (user_id, batch),
        )
    conn.execute(
        "INSERT INTO identity.batch_enrollments (user_id, batch_id) VALUES (%s, %s)",
        (outsider_row[0], other_batch),
    )
    conn.execute(
        "INSERT INTO identity.trainer_assignments (trainer_id, batch_id) VALUES (%s, %s)",
        (trainer_row[0], batch),
    )

    return {
        "batch": batch,
        "other_batch": other_batch,
        "students": [r[0] for r in student_rows],
        "student_pids": [r[1] for r in student_rows],
        "trainer": trainer_row[0],
        "unassigned_trainer": unassigned_row[0],
        "outsider": outsider_row[0],
    }


@pytest.fixture
def connect_as(migrated_db: str, psycopg):
    """Open a connection authenticated as one of the service login roles.

    Connecting as the real role is the only way to test a GRANT. A test that
    runs as the owner proves nothing, because the owner can do everything.
    """
    opened = []

    def _connect(login: str):
        base = migrated_db.split("://", 1)[1]
        _, hostpart = base.split("@", 1)
        conn = psycopg.connect(
            f"postgresql://{login}:{TEST_PASSWORD}@{hostpart}", autocommit=True
        )
        opened.append(conn)
        return conn

    yield _connect

    for conn in opened:
        conn.close()
