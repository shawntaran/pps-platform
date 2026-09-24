"""Identity zone: the only place a student is nameable.

Revision ID: 0002
Revises: 0001

Every direct identifier is stored as ``bytea`` holding an AES-256-GCM token
produced by ``pps_privacy.crypto``. There is deliberately no plaintext ``name``
or ``email`` column anywhere in this zone -- not "we agree not to use one", but
no column to use. Lookups go through the ``_bidx`` blind-index columns.

Each row carries its own ``wrapped_dek``. Deleting that one value is how a
student is erased: every copy of their data, including copies in snapshots and
S3 object versions we cannot enumerate, becomes unreadable at once.
"""

from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION identity.touch_updated_at() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END
        $$
        """
    )

    # Retention policy in one place, so it cannot drift between the expiry job,
    # the privacy notice and whatever someone hardcodes later.
    # Decided with the lead: graduation date + 6 months. The 12-month cap from
    # upload applies when there is no batch, so nothing is retained forever by
    # the simple omission of a graduation date.
    op.execute(
        """
        CREATE FUNCTION identity.retention_expiry(
            graduation_date date,
            created_at timestamptz
        ) RETURNS timestamptz
        LANGUAGE sql IMMUTABLE AS $$
            SELECT CASE
                WHEN graduation_date IS NULL
                    THEN created_at + interval '12 months'
                ELSE (graduation_date + interval '6 months')::timestamptz
            END
        $$
        """
    )

    op.execute(
        """
        CREATE TABLE identity.batches (
            batch_id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name                    text NOT NULL,
            programme               text NOT NULL,
            institution             text NOT NULL,
            starts_on               date,
            ends_on                 date,
            -- Authoritative source of the retention clock. A batch-level date
            -- is harder to game than a self-declared one and expires a whole
            -- cohort consistently.
            graduation_date         date NOT NULL,
            -- Lets a programme run trainers in pseudonymous-only mode. Default
            -- ON per the lead's spec; the field allowlist still applies.
            trainer_identity_access boolean NOT NULL DEFAULT true,
            created_at              timestamptz NOT NULL DEFAULT now(),
            updated_at              timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE identity.users (
            user_id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            -- The bridge to the analysis zone. Random and unrelated to user_id,
            -- so holding one does not yield the other.
            candidate_pid         uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            role                  text NOT NULL
                                  CHECK (role IN ('student','trainer','recruiter','admin','dpo')),

            -- Encrypted identifiers. No plaintext equivalent exists by design.
            name_enc              bytea NOT NULL,
            student_ref_enc       bytea,
            student_ref_bidx      text,
            inst_email_enc        bytea,
            inst_email_bidx       text,
            personal_email_enc    bytea,
            personal_email_bidx   text,
            phone_enc             bytea,

            -- Destroying this erases the user, wherever copies of their
            -- ciphertext happen to live.
            wrapped_dek           bytea NOT NULL,

            status                text NOT NULL DEFAULT 'active'
                                  CHECK (status IN ('active','suspended','expired','erased')),
            -- Overrides the batch graduation date for someone who leaves early.
            graduation_date_override date,
            created_at            timestamptz NOT NULL DEFAULT now(),
            updated_at            timestamptz NOT NULL DEFAULT now(),

            -- A blind index without its ciphertext is a searchable value we
            -- cannot read back, and a ciphertext without its index is
            -- unfindable. Neither half is useful alone, so require both.
            CONSTRAINT student_ref_pair  CHECK ((student_ref_enc IS NULL) = (student_ref_bidx IS NULL)),
            CONSTRAINT inst_email_pair   CHECK ((inst_email_enc IS NULL) = (inst_email_bidx IS NULL)),
            CONSTRAINT personal_email_pair CHECK ((personal_email_enc IS NULL) = (personal_email_bidx IS NULL))
        )
        """
    )
    # Partial unique indexes: one account per institutional address, while
    # still allowing many rows to have none.
    op.execute(
        "CREATE UNIQUE INDEX users_inst_email_bidx_key ON identity.users (inst_email_bidx) "
        "WHERE inst_email_bidx IS NOT NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX users_student_ref_bidx_key ON identity.users (student_ref_bidx) "
        "WHERE student_ref_bidx IS NOT NULL"
    )
    # Personal email is intentionally NOT unique: a student may share a family
    # address, and rejecting that would leak that the address is already known.
    op.execute(
        "CREATE INDEX users_personal_email_bidx_idx ON identity.users (personal_email_bidx) "
        "WHERE personal_email_bidx IS NOT NULL"
    )
    op.execute(
        "CREATE TRIGGER users_touch BEFORE UPDATE ON identity.users "
        "FOR EACH ROW EXECUTE FUNCTION identity.touch_updated_at()"
    )
    op.execute(
        "CREATE TRIGGER batches_touch BEFORE UPDATE ON identity.batches "
        "FOR EACH ROW EXECUTE FUNCTION identity.touch_updated_at()"
    )

    # Credentials live in their own table so they can be granted separately.
    # No role in the access matrix reads this -- not admin, not the DPO.
    op.execute(
        """
        CREATE TABLE identity.credentials (
            user_id             uuid PRIMARY KEY
                                REFERENCES identity.users(user_id) ON DELETE CASCADE,
            password_hash       text NOT NULL,   -- Argon2id, never reversible
            mfa_secret_enc      bytea,
            password_changed_at timestamptz NOT NULL DEFAULT now(),
            updated_at          timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE identity.batch_enrollments (
            user_id    uuid NOT NULL REFERENCES identity.users(user_id) ON DELETE CASCADE,
            batch_id   uuid NOT NULL REFERENCES identity.batches(batch_id) ON DELETE CASCADE,
            status     text NOT NULL DEFAULT 'enrolled'
                       CHECK (status IN ('enrolled','withdrawn','graduated')),
            enrolled_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (user_id, batch_id)
        )
        """
    )
    op.execute("CREATE INDEX batch_enrollments_batch_idx ON identity.batch_enrollments (batch_id)")

    op.execute(
        """
        CREATE TABLE identity.trainer_assignments (
            trainer_id  uuid NOT NULL REFERENCES identity.users(user_id) ON DELETE CASCADE,
            batch_id    uuid NOT NULL REFERENCES identity.batches(batch_id) ON DELETE CASCADE,
            assigned_at timestamptz NOT NULL DEFAULT now(),
            -- Time-bounded on purpose: when this is set, access stops, including
            -- to batches the trainer used to teach. Revocation is an UPDATE, so
            -- the history of who had access when survives for the audit trail.
            revoked_at  timestamptz,
            PRIMARY KEY (trainer_id, batch_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX trainer_assignments_active_idx "
        "ON identity.trainer_assignments (trainer_id, batch_id) WHERE revoked_at IS NULL"
    )

    op.execute(
        """
        CREATE TABLE identity.resumes (
            resume_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     uuid NOT NULL REFERENCES identity.users(user_id) ON DELETE CASCADE,
            resume_pid  uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            -- Pointer only. The file lives in S3, encrypted under wrapped_dek;
            -- extracted text is never persisted, it exists only in worker memory.
            s3_key      text NOT NULL,
            wrapped_dek bytea NOT NULL,
            sha256      bytea NOT NULL,
            byte_size   bigint NOT NULL CHECK (byte_size > 0),
            uploaded_at timestamptz NOT NULL DEFAULT now(),
            expires_at  timestamptz NOT NULL
        )
        """
    )
    op.execute("CREATE INDEX resumes_user_idx ON identity.resumes (user_id)")
    # Drives the retention sweep.
    op.execute("CREATE INDEX resumes_expiry_idx ON identity.resumes (expires_at)")

    op.execute(
        """
        CREATE TABLE identity.submissions (
            submission_id  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id        uuid NOT NULL REFERENCES identity.users(user_id) ON DELETE CASCADE,
            batch_id       uuid NOT NULL REFERENCES identity.batches(batch_id) ON DELETE CASCADE,
            resume_id      uuid REFERENCES identity.resumes(resume_id) ON DELETE SET NULL,
            submission_pid uuid NOT NULL UNIQUE DEFAULT gen_random_uuid(),
            -- A job description is not personal data about the student, but it
            -- does reveal what they are targeting, so it stays in this zone.
            jd_text        text,
            status         text NOT NULL DEFAULT 'submitted'
                           CHECK (status IN ('submitted','processing','analysed','failed','withdrawn')),
            submitted_at   timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX submissions_batch_idx ON identity.submissions (batch_id)")
    op.execute("CREATE INDEX submissions_user_idx ON identity.submissions (user_id)")


def downgrade() -> None:
    for table in (
        "submissions",
        "resumes",
        "trainer_assignments",
        "batch_enrollments",
        "credentials",
        "users",
        "batches",
    ):
        op.execute(f"DROP TABLE IF EXISTS identity.{table} CASCADE")
    op.execute("DROP FUNCTION IF EXISTS identity.retention_expiry(date, timestamptz)")
    op.execute("DROP FUNCTION IF EXISTS identity.touch_updated_at()")
