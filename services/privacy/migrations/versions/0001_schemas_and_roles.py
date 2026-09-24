"""Three data zones and the roles that separate them.

Revision ID: 0001
Revises:

The zone split from docs/privacy/phase1-notes.md section 3 is enforced here by
PostgreSQL privileges, not by application convention:

    identity    names, emails, phones, resume pointers, batch membership
    analysis    scores and derived data, keyed only by pseudonymous IDs
    compliance  consent, audit, DSR and deletion records

The property worth protecting is that ``pps_analysis`` has no route to a name.
It is not merely "the analysis code does not select identity columns" -- the
role has no USAGE on the identity schema at all, so a bug, an injection or a
careless join fails with a permission error instead of returning a student.

Roles are cluster-wide in PostgreSQL. On RDS, creating them needs the
rds_superuser role; run this migration as the provisioning user, not as an
application user.
"""

from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

ROLES = ("pps_identity", "pps_analysis", "pps_compliance", "pps_auth")


def upgrade() -> None:
    # gen_random_uuid() is built in from PostgreSQL 13; pgcrypto is only needed
    # on older servers. We deliberately do NOT use pgcrypto for column
    # encryption -- keys passed through SQL land in pg_stat_statements and in
    # query logs. Encryption happens in the application (pps_privacy.crypto).
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    for role in ROLES:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                    CREATE ROLE {role} NOLOGIN;
                END IF;
            END
            $$
            """
        )

    for schema in ("identity", "analysis", "compliance"):
        op.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        # PUBLIC gets nothing anywhere. Without this, every role in the cluster
        # inherits access it was never granted.
        op.execute(f"REVOKE ALL ON SCHEMA {schema} FROM PUBLIC")

    # Each role sees exactly one zone. The omissions are the point:
    # pps_analysis is never granted USAGE on identity or compliance.
    op.execute("GRANT USAGE ON SCHEMA identity TO pps_identity")
    op.execute("GRANT USAGE ON SCHEMA analysis TO pps_analysis")
    op.execute("GRANT USAGE ON SCHEMA compliance TO pps_compliance")
    # pps_auth reaches only the credentials table (granted in 0004), not the
    # rest of identity -- authentication never needs to read a student name.
    op.execute("GRANT USAGE ON SCHEMA identity TO pps_auth")

    # Legacy default: PUBLIC could create objects in public on PostgreSQL < 15.
    op.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")


def downgrade() -> None:
    for schema in ("compliance", "analysis", "identity"):
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    # Roles are intentionally left in place: they are cluster-wide and may be
    # granted to login users that this migration knows nothing about. Dropping
    # them could break an unrelated database on the same cluster.
