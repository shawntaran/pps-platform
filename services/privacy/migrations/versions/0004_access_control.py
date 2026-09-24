"""Grants, row-level security and the trainer field allowlist.

Revision ID: 0004
Revises: 0003

This is where the access matrix in docs/privacy/phase1-notes.md section 2.4
stops being a table in a document and becomes something the database enforces.

Three mechanisms, doing three different jobs:

* **Grants** decide which role may touch which table at all. This is what keeps
  ``pps_analysis`` away from names and everything away from password hashes.
* **Row-level security** decides which rows. This is the batch scope: a trainer
  sees students in batches they are currently assigned to, and no others.
* **A view** decides which columns. RLS cannot express "this role may read
  ``name_enc`` but not ``phone_enc``", so the trainer-facing surface is a view
  listing exactly the allowed fields.

Requires PostgreSQL 15 or newer for ``security_invoker`` views. Without it a
view runs with its owner's privileges and would silently bypass the RLS
policies below -- which would be worse than having no view at all.

**RLS is the second line, not the first.** Every API route still has to check
authorisation itself; see risk R6 in the notes. What this buys us is that a
missed check in application code fails closed instead of returning a student.

The session context (``app.actor_id``, ``app.actor_role``) must be set with
``SET LOCAL`` inside the request transaction, and must come from the verified
session -- never from a request parameter, a header or anything else a caller
can choose.
"""

from __future__ import annotations

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

RLS_TABLES = (
    "identity.users",
    "identity.resumes",
    "identity.submissions",
    "analysis.analyses",
    "analysis.trainer_reviews",
)


def upgrade() -> None:
    # --- session context helpers ---------------------------------------
    # The third argument to current_setting() makes a missing setting return
    # NULL instead of raising, so an unconfigured session sees no rows rather
    # than erroring in a way someone might be tempted to "fix" by disabling RLS.
    op.execute(
        """
        CREATE FUNCTION identity.current_actor_id() RETURNS uuid
        LANGUAGE sql STABLE AS $$
            SELECT nullif(current_setting('app.actor_id', true), '')::uuid
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION identity.current_actor_role() RETURNS text
        LANGUAGE sql STABLE AS $$
            SELECT coalesce(nullif(current_setting('app.actor_role', true), ''), 'anonymous')
        $$
        """
    )

    # --- grants ---------------------------------------------------------
    op.execute(
        """
        GRANT SELECT, INSERT, UPDATE, DELETE ON
            identity.users, identity.batches, identity.batch_enrollments,
            identity.trainer_assignments, identity.resumes, identity.submissions
        TO pps_identity
        """
    )

    # Password hashes and MFA secrets are reachable by exactly one role, and it
    # is not the one that serves the application. Nothing in the access matrix
    # -- not admin, not the DPO -- can read this table.
    op.execute("REVOKE ALL ON identity.credentials FROM pps_identity")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON identity.credentials TO pps_auth")

    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON analysis.analyses, analysis.trainer_reviews TO pps_analysis")

    # Append-only tables: no UPDATE, no DELETE. The triggers from 0003 are the
    # backstop; withholding the privilege is the primary control.
    op.execute("GRANT SELECT, INSERT ON compliance.consent_records, compliance.audit_log, compliance.deletion_ledger TO pps_compliance")
    op.execute("GRANT SELECT, INSERT ON compliance.policy_versions TO pps_compliance")
    op.execute("GRANT SELECT, INSERT, UPDATE ON compliance.dsr_requests TO pps_compliance")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE compliance.audit_log_event_id_seq TO pps_compliance")

    # --- row-level security ---------------------------------------------
    for table in RLS_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        # FORCE so the policies apply to the table owner too. Without it, any
        # session that happens to connect as the owner sees everything.
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # Students: their own row, always.
    op.execute(
        """
        CREATE POLICY users_self ON identity.users
        FOR SELECT USING (user_id = identity.current_actor_id())
        """
    )

    # Trainers: students enrolled in a batch they are *currently* assigned to,
    # and only where the programme has identity access switched on.
    #
    # Three conditions have to hold, and each one is a decision recorded in the
    # notes: the assignment must not be revoked (access ends when teaching
    # does), the student must be enrolled in that batch, and the batch must
    # permit identity access at all.
    op.execute(
        """
        CREATE POLICY users_trainer_batch ON identity.users
        FOR SELECT USING (
            identity.current_actor_role() = 'trainer'
            AND EXISTS (
                SELECT 1
                FROM identity.batch_enrollments be
                JOIN identity.trainer_assignments ta ON ta.batch_id = be.batch_id
                JOIN identity.batches b ON b.batch_id = be.batch_id
                WHERE be.user_id = identity.users.user_id
                  AND ta.trainer_id = identity.current_actor_id()
                  AND ta.revoked_at IS NULL
                  AND b.trainer_identity_access
            )
        )
        """
    )

    # Background jobs (retention sweep, deletion) need to see every row.
    #
    # This is the one policy that grants broad visibility, so it is also the one
    # to be careful with: 'system' must only ever be set by a background worker
    # whose connection is not reachable from a request path. If user input can
    # ever influence app.actor_role, this policy is the way out of the whole
    # scheme.
    op.execute(
        """
        CREATE POLICY users_system ON identity.users
        FOR ALL USING (identity.current_actor_role() = 'system')
        """
    )

    # Students write their own rows; the system writes any.
    op.execute(
        """
        CREATE POLICY users_self_write ON identity.users
        FOR UPDATE USING (user_id = identity.current_actor_id())
        """
    )

    for table, owner_column in (
        ("identity.resumes", "user_id"),
        ("identity.submissions", "user_id"),
    ):
        short = table.split(".")[1]
        op.execute(
            f"""
            CREATE POLICY {short}_self ON {table}
            FOR ALL USING ({owner_column} = identity.current_actor_id())
            """
        )
        op.execute(
            f"""
            CREATE POLICY {short}_system ON {table}
            FOR ALL USING (identity.current_actor_role() = 'system')
            """
        )

    # Trainers reach resumes and submissions through batch membership, on the
    # same three conditions as above.
    op.execute(
        """
        CREATE POLICY resumes_trainer_batch ON identity.resumes
        FOR SELECT USING (
            identity.current_actor_role() = 'trainer'
            AND EXISTS (
                SELECT 1
                FROM identity.batch_enrollments be
                JOIN identity.trainer_assignments ta ON ta.batch_id = be.batch_id
                JOIN identity.batches b ON b.batch_id = be.batch_id
                WHERE be.user_id = identity.resumes.user_id
                  AND ta.trainer_id = identity.current_actor_id()
                  AND ta.revoked_at IS NULL
                  AND b.trainer_identity_access
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY submissions_trainer_batch ON identity.submissions
        FOR SELECT USING (
            identity.current_actor_role() = 'trainer'
            AND EXISTS (
                SELECT 1
                FROM identity.trainer_assignments ta
                WHERE ta.batch_id = identity.submissions.batch_id
                  AND ta.trainer_id = identity.current_actor_id()
                  AND ta.revoked_at IS NULL
            )
        )
        """
    )

    # Analysis zone. Note it cannot check enrollment -- that lives in the
    # identity zone, which this role cannot reach by design. Scoping here is by
    # batch_id, which is why that column is carried (see 0003).
    op.execute(
        """
        CREATE POLICY analyses_scope ON analysis.analyses
        FOR ALL USING (
            identity.current_actor_role() = 'system'
            OR candidate_pid = nullif(current_setting('app.candidate_pid', true), '')::uuid
            OR (
                identity.current_actor_role() = 'trainer'
                AND batch_id = ANY (
                    string_to_array(
                        coalesce(nullif(current_setting('app.trainer_batches', true), ''), ''),
                        ','
                    )::uuid[]
                )
            )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY trainer_reviews_scope ON analysis.trainer_reviews
        FOR ALL USING (
            identity.current_actor_role() = 'system'
            OR candidate_pid = nullif(current_setting('app.candidate_pid', true), '')::uuid
            OR (
                identity.current_actor_role() = 'trainer'
                AND batch_id = ANY (
                    string_to_array(
                        coalesce(nullif(current_setting('app.trainer_batches', true), ''), ''),
                        ','
                    )::uuid[]
                )
            )
        )
        """
    )

    # --- the trainer field allowlist ------------------------------------
    # Exactly the fields the lead specified: name, student ID, institutional
    # email, submission status. Personal email, phone, address and the rest of
    # the profile are absent -- not filtered in application code, absent from
    # the relation the trainer is allowed to query.
    #
    # security_invoker makes the RLS policies above run as the querying session,
    # so the batch scope still applies through the view. security_barrier stops
    # a cheap user-supplied function in a WHERE clause from being evaluated
    # before the scope predicate and leaking rows through its arguments.
    op.execute(
        """
        CREATE VIEW identity.trainer_student_view
        WITH (security_invoker = true, security_barrier = true) AS
        SELECT
            u.user_id,
            u.candidate_pid,
            u.name_enc,
            u.student_ref_enc,
            u.inst_email_enc,
            u.wrapped_dek,
            be.batch_id,
            be.status AS enrollment_status
        FROM identity.users u
        JOIN identity.batch_enrollments be ON be.user_id = u.user_id
        WHERE u.role = 'student'
        """
    )
    op.execute("GRANT SELECT ON identity.trainer_student_view TO pps_identity")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS identity.trainer_student_view")

    for policy, table in (
        ("analyses_scope", "analysis.analyses"),
        ("trainer_reviews_scope", "analysis.trainer_reviews"),
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
    ):
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table}")

    for table in RLS_TABLES:
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute("DROP FUNCTION IF EXISTS identity.current_actor_role()")
    op.execute("DROP FUNCTION IF EXISTS identity.current_actor_id()")
