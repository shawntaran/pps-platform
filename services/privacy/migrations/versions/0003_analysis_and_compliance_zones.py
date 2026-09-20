"""Analysis and compliance zones.

Revision ID: 0003
Revises: 0002

Two things here are easy to "fix" into uselessness, so both are stated loudly:

1. The analysis zone has NO foreign keys into identity. That is not an
   oversight. A foreign key would require the analysis role to reach the
   identity schema, which is exactly the separation we are buying. Referential
   integrity across the zone boundary is maintained by the application and by
   the deletion sweep, at the cost of a constraint the database cannot enforce.
   Adding ``REFERENCES identity.users`` here would collapse the design.

2. Consent and audit records are append-only. Withdrawing consent inserts a new
   row; it never edits the old one. Proving what someone agreed to, and when,
   depends on nothing having been rewritten afterwards.
"""

from __future__ import annotations

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- analysis zone -------------------------------------------------
    op.execute(
        """
        CREATE TABLE analysis.analyses (
            analysis_id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),

            -- Pseudonymous references only. Deliberately not foreign keys:
            -- see the module docstring.
            candidate_pid     uuid NOT NULL,
            resume_pid        uuid NOT NULL,
            submission_pid    uuid,
            -- Carried so trainer batch-scoping can be enforced in the database
            -- rather than only in application code. A batch identifies a cohort
            -- of many students, so it narrows the anonymity set only mildly;
            -- we judged database-level scoping the better trade. It is the one
            -- non-pseudonymous value in this zone -- do not add more.
            batch_id          uuid NOT NULL,

            skills            jsonb NOT NULL DEFAULT '[]'::jsonb,
            scores            jsonb NOT NULL DEFAULT '{}'::jsonb,
            issues            jsonb NOT NULL DEFAULT '[]'::jsonb,
            recommendations   jsonb NOT NULL DEFAULT '[]'::jsonb,

            -- Provenance. Art. 22 and the EU AI Act both turn on being able to
            -- say which model produced a given result, and we need to know
            -- which redaction build was in force if a leak is ever found.
            model_id          text NOT NULL,
            model_version     text NOT NULL,
            prompt_version    text NOT NULL,
            redaction_version text NOT NULL,
            -- What was sent to the provider, recorded as a field list plus a
            -- hash rather than the content itself -- storing the prompt would
            -- recreate the data we just avoided persisting.
            egress_fields     jsonb NOT NULL DEFAULT '[]'::jsonb,
            egress_hash       bytea,

            created_at        timestamptz NOT NULL DEFAULT now(),
            expires_at        timestamptz NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX analyses_candidate_idx ON analysis.analyses (candidate_pid)")
    op.execute("CREATE INDEX analyses_batch_idx ON analysis.analyses (batch_id)")
    op.execute("CREATE INDEX analyses_expiry_idx ON analysis.analyses (expires_at)")

    op.execute(
        """
        CREATE TABLE analysis.trainer_reviews (
            review_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            analysis_id   uuid NOT NULL REFERENCES analysis.analyses(analysis_id) ON DELETE CASCADE,
            candidate_pid uuid NOT NULL,
            batch_id      uuid NOT NULL,
            -- The trainer is staff, so this is their user_id. Still not a
            -- foreign key: the constraint would cross the zone boundary.
            trainer_id    uuid NOT NULL,
            comments      text,
            score         numeric(5, 2) CHECK (score >= 0 AND score <= 100),
            created_at    timestamptz NOT NULL DEFAULT now(),
            updated_at    timestamptz NOT NULL DEFAULT now(),
            expires_at    timestamptz NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX trainer_reviews_candidate_idx ON analysis.trainer_reviews (candidate_pid)")
    op.execute("CREATE INDEX trainer_reviews_batch_idx ON analysis.trainer_reviews (batch_id)")

    # --- compliance zone -----------------------------------------------
    op.execute(
        """
        CREATE FUNCTION compliance.reject_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION
                'table %.% is append-only; record a new row instead of changing this one',
                TG_TABLE_SCHEMA, TG_TABLE_NAME
                USING ERRCODE = 'restrict_violation';
        END
        $$
        """
    )

    op.execute(
        """
        CREATE TABLE compliance.policy_versions (
            version      text PRIMARY KEY,
            published_at timestamptz NOT NULL DEFAULT now(),
            -- Hash of the exact notice text shown, so we can prove later what a
            -- given version actually said.
            text_hash    bytea NOT NULL,
            notes        text
        )
        """
    )

    op.execute(
        """
        CREATE TABLE compliance.consent_records (
            consent_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            -- Pseudonymous, so the consent log survives erasure of the rest of
            -- the record as minimal proof that consent existed.
            subject_pid    uuid NOT NULL,
            purpose_code   text NOT NULL,
            action         text NOT NULL CHECK (action IN ('granted','withdrawn')),
            -- Per-request scope, e.g. which recruiter and until when.
            scope          jsonb NOT NULL DEFAULT '{}'::jsonb,
            policy_version text NOT NULL REFERENCES compliance.policy_versions(version),
            notice_hash    bytea NOT NULL,
            ui_version     text,
            occurred_at    timestamptz NOT NULL DEFAULT now(),
            -- HMAC of the IP, not the IP. Proves the event without keeping a
            -- location trail for every consent click.
            ip_hash        bytea
        )
        """
    )
    op.execute(
        "CREATE INDEX consent_records_lookup_idx "
        "ON compliance.consent_records (subject_pid, purpose_code, occurred_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE compliance.dsr_requests (
            request_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            subject_pid uuid NOT NULL,
            type        text NOT NULL
                        CHECK (type IN ('access','rectification','erasure','portability','restriction','objection')),
            status      text NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open','in_progress','completed','refused')),
            opened_at   timestamptz NOT NULL DEFAULT now(),
            -- One month is the statutory response window under GDPR; DPDP has
            -- its own timeline. Stored per request so a change in policy does
            -- not retroactively move an existing deadline.
            due_at      timestamptz NOT NULL,
            closed_at   timestamptz,
            outcome     text
        )
        """
    )
    op.execute("CREATE INDEX dsr_requests_open_idx ON compliance.dsr_requests (due_at) WHERE closed_at IS NULL")

    op.execute(
        """
        CREATE TABLE compliance.deletion_ledger (
            -- Hashed so the ledger itself is not a list of who we deleted.
            subject_hash bytea PRIMARY KEY,
            deleted_at   timestamptz NOT NULL DEFAULT now(),
            reason       text NOT NULL
                         CHECK (reason IN ('user_request','retention_expiry','withdrawal','admin'))
        )
        """
    )

    op.execute(
        """
        CREATE TABLE compliance.audit_log (
            event_id    bigserial PRIMARY KEY,
            occurred_at timestamptz NOT NULL DEFAULT now(),
            actor_id    uuid,
            actor_role  text NOT NULL,
            action      text NOT NULL,
            subject_pid uuid,
            -- Which fields were seen, never their values. An audit log that
            -- records the data it is auditing becomes a second copy of it.
            field_set   jsonb NOT NULL DEFAULT '[]'::jsonb,
            context     jsonb NOT NULL DEFAULT '{}'::jsonb
        )
        """
    )
    op.execute("CREATE INDEX audit_log_subject_idx ON compliance.audit_log (subject_pid, occurred_at DESC)")
    op.execute("CREATE INDEX audit_log_actor_idx ON compliance.audit_log (actor_id, occurred_at DESC)")

    # Append-only, enforced twice: the grants in 0004 withhold UPDATE and
    # DELETE, and these triggers stop anything that still gets through --
    # including a session connected as the table owner.
    for table in ("consent_records", "audit_log", "deletion_ledger"):
        op.execute(
            f"""
            CREATE TRIGGER {table}_append_only
            BEFORE UPDATE OR DELETE ON compliance.{table}
            FOR EACH ROW EXECUTE FUNCTION compliance.reject_mutation()
            """
        )


def downgrade() -> None:
    for table in ("audit_log", "deletion_ledger", "dsr_requests", "consent_records", "policy_versions"):
        op.execute(f"DROP TABLE IF EXISTS compliance.{table} CASCADE")
    op.execute("DROP FUNCTION IF EXISTS compliance.reject_mutation()")
    for table in ("trainer_reviews", "analyses"):
        op.execute(f"DROP TABLE IF EXISTS analysis.{table} CASCADE")
