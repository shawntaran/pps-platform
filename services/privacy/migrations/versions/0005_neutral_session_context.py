"""Move the session-context helpers out of the identity schema.

Revision ID: 0005
Revises: 0004

Fixes a latent trap introduced in 0004.

The row-level security policies on the *analysis* tables called
``identity.current_actor_role()``. The analysis role has no USAGE on the
identity schema -- that is the whole point of the zone split -- so those calls
should have been refused. They were not, and the policies worked.

The reason they worked is that both helpers are simple ``LANGUAGE sql STABLE``
functions, so PostgreSQL *inlines* them into the query plan. Inlining erases
the schema reference before permissions are checked at run time. Calling the
same function directly as the analysis role fails with "permission denied for
schema identity", which is what proves the policies were relying on inlining
rather than on having access.

That is fragile in a way that would fail badly and late. Rewriting either
helper as PL/pgSQL -- an entirely natural change, and the obvious move the
first time someone wants an IF statement in there -- stops the inlining and
breaks every analysis-zone query in production, with an error that points at
schema permissions rather than at the edit that caused it.

So the helpers move to a neutral ``app_context`` schema that every service role
may use. This costs nothing in separation: the functions read session settings
and touch no tables, so granting USAGE on the schema that holds them grants
access to no data at all.
"""

from __future__ import annotations

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

ROLES = ("pps_identity", "pps_analysis", "pps_compliance", "pps_auth")

# Every policy from 0004 that referenced the old helpers, and so has to be
# rebuilt against the new ones.
POLICIES = (
    ("users_self", "identity.users"),
    ("users_self_write", "identity.users"),
    ("users_trainer_batch", "identity.users"),
    ("users_system", "identity.users"),
    ("resumes_self", "identity.resumes"),
    ("resumes_system", "identity.resumes"),
    ("resumes_trainer_batch", "identity.resumes"),
    ("submissions_self", "identity.submissions"),
    ("submissions_system", "identity.submissions"),
    ("submissions_trainer_batch", "identity.submissions"),
    ("analyses_scope", "analysis.analyses"),
    ("trainer_reviews_scope", "analysis.trainer_reviews"),
)

_BATCH_ARRAY = (
    "string_to_array("
    "coalesce(nullif(current_setting('app.trainer_batches', true), ''), ''), ','"
    ")::uuid[]"
)


def _analysis_policy(name: str, table: str) -> str:
    return f"""
        CREATE POLICY {name} ON {table}
        FOR ALL USING (
            app_context.actor_role() = 'system'
            OR candidate_pid = nullif(current_setting('app.candidate_pid', true), '')::uuid
            OR (
                app_context.actor_role() = 'trainer'
                AND batch_id = ANY ({_BATCH_ARRAY})
            )
        )
    """


def _trainer_batch_policy(name: str, table: str, user_column: str) -> str:
    """Trainer access to an identity-zone table, via live batch membership.

    Note this does not consult ``app.trainer_batches``: inside the identity
    zone the database can check assignments itself, so scoping does not depend
    on the caller passing the right value. The analysis zone cannot do that --
    it has no route to the identity schema -- which is why it uses the session
    setting instead. The asymmetry is deliberate.
    """
    return f"""
        CREATE POLICY {name} ON {table}
        FOR SELECT USING (
            app_context.actor_role() = 'trainer'
            AND EXISTS (
                SELECT 1
                FROM identity.batch_enrollments be
                JOIN identity.trainer_assignments ta ON ta.batch_id = be.batch_id
                JOIN identity.batches b ON b.batch_id = be.batch_id
                WHERE be.user_id = {table}.{user_column}
                  AND ta.trainer_id = app_context.actor_id()
                  AND ta.revoked_at IS NULL
                  AND b.trainer_identity_access
            )
        )
    """


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS app_context")
    op.execute("REVOKE ALL ON SCHEMA app_context FROM PUBLIC")
    for role in ROLES:
        op.execute(f"GRANT USAGE ON SCHEMA app_context TO {role}")

    op.execute(
        """
        CREATE OR REPLACE FUNCTION app_context.actor_id() RETURNS uuid
        LANGUAGE sql STABLE AS $$
            SELECT nullif(current_setting('app.actor_id', true), '')::uuid
        $$
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION app_context.actor_role() RETURNS text
        LANGUAGE sql STABLE AS $$
            SELECT coalesce(nullif(current_setting('app.actor_role', true), ''), 'anonymous')
        $$
        """
    )
    for fn in ("actor_id()", "actor_role()"):
        op.execute(f"GRANT EXECUTE ON FUNCTION app_context.{fn} TO PUBLIC")

    for policy, table in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table}")

    op.execute("DROP FUNCTION IF EXISTS identity.current_actor_role()")
    op.execute("DROP FUNCTION IF EXISTS identity.current_actor_id()")

    # Rebuilt identically, against the neutral helpers.
    op.execute(
        """
        CREATE POLICY users_self ON identity.users
        FOR SELECT USING (user_id = app_context.actor_id())
        """
    )
    op.execute(
        """
        CREATE POLICY users_self_write ON identity.users
        FOR UPDATE USING (user_id = app_context.actor_id())
        """
    )
    op.execute(_trainer_batch_policy("users_trainer_batch", "identity.users", "user_id"))
    op.execute(
        """
        CREATE POLICY users_system ON identity.users
        FOR ALL USING (app_context.actor_role() = 'system')
        """
    )

    for table, short in (("identity.resumes", "resumes"), ("identity.submissions", "submissions")):
        op.execute(
            f"""
            CREATE POLICY {short}_self ON {table}
            FOR ALL USING (user_id = app_context.actor_id())
            """
        )
        op.execute(
            f"""
            CREATE POLICY {short}_system ON {table}
            FOR ALL USING (app_context.actor_role() = 'system')
            """
        )

    op.execute(_trainer_batch_policy("resumes_trainer_batch", "identity.resumes", "user_id"))
    op.execute(
        """
        CREATE POLICY submissions_trainer_batch ON identity.submissions
        FOR SELECT USING (
            app_context.actor_role() = 'trainer'
            AND EXISTS (
                SELECT 1
                FROM identity.trainer_assignments ta
                WHERE ta.batch_id = identity.submissions.batch_id
                  AND ta.trainer_id = app_context.actor_id()
                  AND ta.revoked_at IS NULL
            )
        )
        """
    )

    op.execute(_analysis_policy("analyses_scope", "analysis.analyses"))
    op.execute(_analysis_policy("trainer_reviews_scope", "analysis.trainer_reviews"))


def downgrade() -> None:
    for policy, table in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table}")
    op.execute("DROP SCHEMA IF EXISTS app_context CASCADE")
    # 0004 recreates its own helpers and policies on the way back down.
