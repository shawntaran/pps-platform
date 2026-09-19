# Phase 1 - GDPR & Privacy Guardrail Layer: pre-coding findings

**Owner:** Shawn | **Branch:** `feature/privacy-layer` | **Status:** DRAFT for team review, no code written yet | **Date:** 2026-09-19

> Engineering notes, not legal advice. Anything marked **[LEGAL]** needs a DPO / counsel check before we rely on it.

Companion doc: [consent-and-notice-draft.md](consent-and-notice-draft.md) (consent form, privacy notice, wireframes).

---

## 0. Decisions I need before I write code

| # | Decision | Who | Status |
|---|----------|-----|--------|
| 1 | AWS region for "localized" storage; LLM provider + region | Rahul (unavailable) | **Open.** Also depends on #4. Built as config (`AWS_REGION`, `LLM_ENDPOINT`), so it doesn't block schema, crypto or PII work. Recommendation unchanged: one region close to most students; LLM via an in-region/EU endpoint under a DPA with no-training and zero/short retention. |
| 2 | Retention after graduation (grace period) | Lead | **Decided: graduation date + 6 months.** Alumni can opt in to longer (fresh consent). |
| 3 | Legal basis: explicit consent for everything, or consent + something else | Lead / [LEGAL] | **Open.** Keep opt-in as requested; see risk R2. |
| 4 | Which countries are the students in, where do recruiters sit, which laws apply | Lead | **Open, being researched.** Decides adequacy / SCCs, and whether local law (e.g. India's DPDP Act) applies on top of GDPR. |
| 5 | Trainer access to identity data | Lead (spec given) + Hemanth | **Decided: batch-scoped field allowlist, spec in 2.4.** Programme toggle kept but now defaults ON. My earlier student-consent gate is **withdrawn** — reasoning in 2.4. |
| 6 | "Encryption mechanism already established": what is it? | Lead / Rahul | **Assumed AES-256 + AWS KMS**, behind a `KeyProvider` interface (KMS in AWS, a local key in dev/test) so nothing waits on AWS setup. Rahul confirms later. |
| 7 | Source of truth for graduation date | Lead | **Mostly answered by the batch model:** `batches.graduation_date` is authoritative, with a per-user override for early leavers and a 12-month cap if there's no batch. Confirm. |

---

## 1. Ground rules I'm designing to

- **Roles (Art. 4, 28).** Institution/platform = controller. AWS and the LLM provider = processors (DPA needed). Recruiters = independent controllers once they receive data. We can gate what they get, not what they do with it afterwards.
- **What we build is pseudonymisation, not anonymisation.** Swapping name/email for tokens while keeping a mapping is still personal data (Recital 26): access, erasure and security duties all still apply. UI copy and docs say "personal details removed", never "anonymous". True anonymisation only applies to aggregate stats with small-cell suppression.
- **One choke point (Art. 25, privacy by design).** Anything leaving our boundary (LLM, recruiter DB, exports) goes through a single *egress gateway* that checks consent and a field allowlist. No other code path may call an external provider.
- **Automated evaluation (Art. 22, EU AI Act).** The ATS score is guidance for the student, never a hiring decision, and a human stays in the loop. Candidate-screening AI is listed as high-risk in EU AI Act Annex III. **[LEGAL]** confirm timing and whether the recruiter-facing part triggers it. A DPIA (Art. 35) is likely warranted.

---

## 2. Data inventory

### 2.1 What a resume contains, and what we actually need

| Item | Class | Needed for analysis? | Rule |
|------|-------|----------------------|------|
| Name | Direct identifier | No | Identity vault only. Never to LLM. |
| Email, phone | Direct identifier | No | Vault only, encrypted. Used for login, notifications, consented reveal. |
| Street address | Direct identifier | No | Drop. Keep country/city only if the user opts in. |
| LinkedIn / GitHub / portfolio URLs | Direct identifier (handle = name) | Rarely | Vault; redact from LLM input. |
| Photo | Special-category risk (ethnicity etc.) | No | Strip images at ingestion. |
| DOB, age, gender, marital status, nationality, religion, parents' names | Protected characteristics / Art. 9 risk | No | Detect + redact, never store. Warn the user. |
| Government IDs (passport, national/tax ID) | Direct identifier | No | Detect, drop, alert the user. |
| References / referees | **Third-party** personal data | No | Drop entirely. |
| Education | Quasi-identifier | Degree, field, grad year | Keep degree/field/year (grad year drives retention). Institution coarse. CGPA optional. |
| Employers, titles, dates | Quasi-identifier | Titles, durations, skills | Employer -> placeholder for LLM (configurable, measure quality impact). |
| Skills, projects, certifications | Low | Yes | Keep. Strip credential IDs / URLs. |
| Free-text summary | Unknown | Yes | Same redaction. May contain health/visa/etc. |
| **File metadata** (author, company, revision history, embedded image EXIF) | Hidden PII | No | Strip on upload. Easy to forget. |
| Derived: skills list, scores, issues, recommendations | Personal data (derived) | n/a | Keyed by pseudonymous ID. Scan LLM output for leaked PII. |
| Submitted job description (JD) | Low, but reveals the student's targets | Yes (match scoring) | Keep with the analysis. Strip any recruiter contact details in it. |
| Trainer comments / scores | **Personal data about the student, authored by staff** | n/a | Zone B, batch-scoped. Disclosable to the student on an access request (see 2.5, Q3). |
| Password / auth data (hashes, MFA secrets, sessions, reset tokens) | Credentials | No | Argon2id hashes. Never returned by any API, to any role, including admin and DPO. Out of scope for every view in 2.4. |
| Operational: IP, user agent, timestamps | Personal data | n/a | Minimise, short retention. |
| Consent records | Personal data (accountability) | n/a | Append-only, minimal fields, retained longer (see 6). |

### 2.2 Data minimisation rules (Art. 5(1)(c))

1. Account collects only: name, email, graduation date/year, programme. Phone optional. No DOB or gender fields.
2. Upload gate: type/size validation, malware scan, strip metadata + images.
3. Redaction runs before anything else touches the text. Extracted raw text is **not persisted**; it lives in worker memory only.
4. Egress gateway is deny-by-default: a per-purpose allowlist of fields. LLM gets redacted text only.
5. Recruiter view = pseudonymous candidate card (skills, degree/field/year, scores only if the student agreed). Identity is revealed per recruiter, per request, with consent.
6. No PII in logs, error trackers, analytics, or URLs. No third-party trackers.
7. Dev/test uses synthetic resumes only (Faker), never real student data.

### 2.3 Where it lives, who touches it, third parties

| Data | Store | Third parties |
|------|-------|---------------|
| Identity (name/email/phone) | Postgres `identity` schema, column-encrypted | AWS (RDS, KMS): processor. Email provider: gets the email address only. |
| Original resume file | S3, app-encrypted + SSE-KMS | AWS |
| Redacted text | Worker memory only | LLM provider (processor): sees redacted text only |
| Analysis | Postgres `analysis` schema | AWS. Recruiters (controllers) see the consented card. |
| Consent / audit / DSR | Postgres `compliance` schema | AWS |
| Logs | CloudWatch, KMS-encrypted, short retention | AWS |

### 2.4 Access matrix (proposal for Hemanth's RBAC)

`own` = own records only. `batch` = **only students in a batch the trainer is currently assigned to**. `(c)` = only with consent. `-` = none.

| Data | Student | Trainer | Recruiter | Admin | DPO |
|------|---------|---------|-----------|-------|-----|
| Name | own | batch | (c) per-request reveal | - (break-glass, audited) | via DSR, audited |
| University / student ID | own | batch | - | manage | via DSR |
| Institutional email | own | batch | (c) reveal | - (break-glass) | via DSR |
| Personal email / phone / address | own | **-** | (c) reveal | - (break-glass) | via DSR |
| Original resume + JD | own | batch | (c) | - | via DSR |
| Submission status | own | batch | - | aggregate | via DSR |
| ATS report / analysis | own | batch | (c) card | aggregate only | via DSR |
| Trainer comments / scores | own (see Q3) | batch, own authored + co-trainers | - | - | via DSR |
| Batch analytics | own position only | batch, **aggregated** | - | aggregate | - |
| Other batches, any field | - | **-** | n/a | scoped | via DSR |
| Account / profile beyond the list above | own | **-** | - | manage | via DSR |
| Password / auth data | - | **-** | - | **-** | **-** |
| Consent log | own | **-** | - | - | read all |
| Access / audit log | own access history | **-** | - | read | read |

Enforcement must be **server-side** (see R6).

### 2.5 Trainer access model (per the lead's spec)

**Principle:** trainers get identity data because academic review needs it, limited to the batch they're assigned to and to the fields that review actually uses. It's an allowlist, not "identity access on/off".

- **Allowed fields:** student name, university/student ID, institutional email, submitted resume and JD, submission status, ATS report, trainer comments and scores.
- **Denied:** passwords and auth data, account/profile fields outside that list, personal (non-institutional) contact details as *stored fields*, any student outside their batches, and system-wide consent/audit records.
- **Resume contact details are visible in practice.** The trainer reviews the real document, so whatever contact details it contains are on screen. We therefore can't claim trainers don't see personal contact details. Two consequences: (1) the privacy notice must say so plainly; (2) it's the *stored, queryable, exportable* personal fields we withhold, which still limits bulk extraction. If you want the stronger version, we can show trainers a contact-masked render by default with a "reveal, and log it" button — more work, and it may hurt review quality, since formatting of the header block is itself part of an ATS critique. **My recommendation: don't mask; disclose instead.**
- **Batch scoping is the security boundary**, enforced at three layers: a role check, a batch-membership check inside every query (not a filter the caller can pass), and Postgres RLS keyed to the trainer's current assignments as defence in depth. Assignments are time-bounded: when `revoked_at` is set, access stops, including for batches they used to teach.
- **Batch analytics are aggregated** with small-cell suppression (hide any group under [5]) so an individual can't be reconstructed from filters. Individual rows only for their own batch.
- **Everything is audit-logged**: who, which student, which field set, when, and why (the view/endpoint). Students see it in "Who saw my data".
- **The programme toggle survives but flips to default ON.** It lets a programme run trainers in pseudonymous-only mode. Worth keeping while the countries/law question (#4) is open, in case a jurisdiction needs it. If you'd rather not carry the branch, say so and I'll drop it.

**Correcting my earlier proposal:** I previously suggested student consent as a second gate on trainer access. **Withdraw that.** If trainer review is a core part of the programme, consent is the wrong legal basis — a student can't meaningfully refuse, which is the same "freely given" problem as R2, and one refusal would break the academic workflow. Trainer review should run on contract/legitimate interest, disclosed in the privacy notice, not on a consent checkbox. Consent stays for the genuinely optional things: recruiters, international transfer, extended retention.

**Open questions on this:**
- **Q1.** Can trainers download or export the resume and ATS report, or only view them in-app? Export is where batch scoping leaks. My recommendation: view in-app, watermarked, no bulk export; a single-file download logged separately.
- **Q2.** Do co-trainers on the same batch see each other's comments and scores? The matrix assumes yes.
- **Q3.** Can students see their own trainer comments and scores? **Note:** even if the institution treats them as internal notes, they're the student's personal data and are generally disclosable under an access request. Better to design them as student-visible than to promise trainers a privacy that won't hold. **[LEGAL]** if you want to argue an exemption.
- **Q4.** Confirm "institutional email" exists as a separate field from personal email. If students sign up with a personal address, this distinction collapses and trainers see the personal one.

---

## 3. PII / analysis separation

Your proposed split is right in spirit. Three changes:

1. `ANALYSIS -> resume_id -> user_id` is a trivial join. Analysis should reference a random `candidate_pid`; the mapping lives only in the identity zone.
2. Don't keep raw content in the DB. The RESUME row holds an encrypted file pointer only.
3. Add a compliance zone (consent, policy versions, DSR requests, deletion ledger, audit).

```
ZONE A: identity   (restricted role: app-identity, break-glass only for humans)
  users(user_id PK, candidate_pid UNIQUE, name_enc, student_ref_enc,
        student_ref_bidx, inst_email_enc, inst_email_bidx, personal_email_enc,
        personal_email_bidx, phone_enc, status, wrapped_dek, created_at)
  batches(batch_id PK, name, programme, institution, starts_on, ends_on,
          graduation_date, trainer_identity_access bool DEFAULT true)
  batch_enrollments(user_id FK, batch_id FK, status, PK(user_id, batch_id))
  trainer_assignments(trainer_id FK, batch_id FK, assigned_at,
                      revoked_at NULL, PK(trainer_id, batch_id))
  submissions(submission_id PK, user_id FK, batch_id FK, submission_pid UNIQUE,
              jd_text, status, submitted_at)
  resumes(resume_id PK, user_id FK, resume_pid UNIQUE, s3_key, wrapped_dek,
          sha256, uploaded_at, expires_at)

  -- auth lives apart from all of it; no role in 2.4 can read it
  credentials(user_id FK, argon2id_hash, mfa_secret_enc, updated_at)

ZONE B: analysis   (broader role; NO user_id, NO name/email/phone anywhere)
  analyses(analysis_id PK, candidate_pid, resume_pid, submission_pid, skills,
           scores, issues, recommendations, model_id, model_version,
           prompt_version, redaction_version, created_at, expires_at)
  trainer_reviews(review_id PK, candidate_pid, analysis_id FK, batch_id,
                  trainer_id, comments, score, created_at, updated_at,
                  expires_at)

ZONE C: compliance (append-only where noted)
  consent_records   (append-only)     -- detail in consent doc
  policy_versions(version, published_at, text_hash)
  dsr_requests(id, subject_pid, type, status, opened_at, due_at, closed_at)
  deletion_ledger(subject_hash, deleted_at)   -- replay after backup restore
  audit_log         (append-only)     -- next phase
```

**How the trainer view crosses the zones — read this before implementing it.** A trainer screen shows the student's name next to their ATS report, which spans zone A and zone B. The wrong fix, and the one someone will reach for, is adding `user_id` or a name column to zone B; that destroys the separation permanently. The right one: a single authorised service resolves `user_id -> candidate_pid` in zone A after checking batch scope, queries zone B by `candidate_pid`, and joins in application memory. Zone B keeps no identity columns, and a leak of the analysis schema alone still yields no names. Same pattern for the recruiter card.

**Graduation date now comes from `batches`, not the student.** That partly answers open decision #7: a batch-level date is authoritative, harder to game than a self-declared one, and it expires a whole cohort consistently. Keep a per-user override for students who leave early, and keep the 12-month hard cap for anyone with no batch.

Isolation: same Postgres instance, separate schemas + roles + row-level security for the MVP. The design allows moving zone A to its own instance later if we need stronger blast-radius control.

Erasure: delete zone A rows, destroy the user's DEK, delete zone B rows via `candidate_pid`, write to `deletion_ledger`. Don't lean on "unlinked = anonymous".

---

## 4. Encryption & key management

| Asset | In transit | At rest | Notes |
|-------|-----------|---------|-------|
| Resume files | TLS 1.2+ (1.3 preferred) | **App-side AES-256-GCM with a per-user data key**, then S3 SSE-KMS on top | Per-user key allows *crypto-shredding*: destroy the key and every copy (versions, backups) is unreadable. |
| Database | `sslmode=verify-full` | RDS storage encryption (KMS CMK). Covers snapshots, replicas, backups | Must be enabled at creation. It can't be switched on in place. |
| Direct identifiers (name/email/phone) | | App-side AES-256-GCM, per-user DEK, AAD = table+column+user_id | Email lookup via blind index (HMAC-SHA-256 with a separate key), never plaintext. |
| Backups | | RDS snapshots on the same CMK, <= 35-day retention, cross-region copies only inside allowed regions | Erasure reaches backups through expiry + crypto-shredding + ledger replay. |
| Logs | TLS | CloudWatch log group encrypted with KMS, fixed retention | Redaction filter in the logger. No request bodies. |
| Secrets | | AWS Secrets Manager / SSM. Never in git | `gitleaks` pre-commit + GitHub push protection. |

Key hierarchy:

```
KMS CMK (per env, per data class: identity-db / resume-files / logs / backups)
   \-- wraps -> per-user DEK (AES-256), stored wrapped next to the record
                  \-- encrypts -> resume file, name/email/phone
```

- Separate CMKs per data class and per environment, least-privilege key policies, automatic rotation on.
- CloudTrail records every `kms:Decrypt`: free audit trail of who decrypted what.
- Keys stay in one region if residency is strict (no multi-region keys).
- **OpenSSL:** use the library, not the tool. TLS already uses it underneath. App-level crypto goes through Python `cryptography` (AES-GCM) or the AWS Encryption SDK. Never shell out to the `openssl` CLI (keys on disk, secrets in argv).

---

## 5. Data lifecycle & retention (proposal)

| Data | Retention | Mechanism | Open |
|------|-----------|-----------|------|
| Account + identity | Graduation + 6 months (**decided**) | Scheduled job, reminder email T-30d | Length of the optional alumni extension (proposed 12 months) |
| Original resume | Same, or immediately on user delete | Destroy per-user DEK, delete object | |
| Analysis | Same as resume (linked) | Cascade on `candidate_pid` | Keep anonymised aggregates? |
| Trainer comments / scores | Same as the analysis they attach to | Cascade on `candidate_pid` | Does the institution need to keep assessment records longer for academic purposes? If so they need their own basis and retention. |
| Redacted text / prompts | Not persisted | Memory only. LLM provider zero-retention | Confirm provider terms |
| Recruiter shares | Expire (e.g. 90 days) or on withdrawal | Expiring access grants | Recruiter contract terms |
| Consent records | Withdrawal/deletion + N years, minimal fields | Kept as proof (Art. 17(3)(e)) | [LEGAL] N |
| Audit / access logs | 12 months, no PII payloads | Log retention setting | |
| Backups | <= 35 days rolling | Automated. After a restore, replay `deletion_ledger` | |
| No graduation date on file | Cap at upload + 12 months | Fallback rule so nothing lives forever | |

---

## 6. Tech stack review

| Proposed | Verdict | Notes |
|----------|---------|-------|
| **Presidio + spaCy** | Keep, with caveats | Runs in our infra, so no PII goes to a third party for detection. Stock recognizers miss resume-specific items, so custom ones are needed: phone formats, LinkedIn/GitHub handles, roll numbers, DOB, regional IDs, "References" blocks. NER recall on resumes is the weak spot (ALL-CAPS names, tables, multi-column layout). Layer it: (1) structural removal of the header/contact block; (2) regex/checksum recognizers; (3) NER, with spaCy `en_core_web_lg` as baseline and a transformer model worth testing; (4) **exact-match scrub using the user's own signup name/email/phone**, cheap and high recall; (5) scan LLM output. |
| Alternatives considered | | AWS Comprehend PII: managed and in-region, but an extra processor, priced per character, limited languages. Optional second pass. Google DLP: outside AWS, no. LLM-based redaction: **rejected**, it sends the PII to the provider we're protecting against. spaCy alone: no anonymiser. |
| **PostgreSQL** | Keep | Use RDS, not self-hosted. Schemas + roles + RLS for zones. `pgAudit` for access logs. App-side column encryption, **not** `pgcrypto` (keys pass through SQL and can land in logs / `pg_stat_statements`). |
| **OpenSSL** | Reframe | See section 4: library only, not the CLI. |
| **AWS KMS** | Keep | Envelope encryption, CMK per data class. Cheap at our scale. Vault/CloudHSM is overkill for now. |
| Additions | Suggest | `gitleaks`, Secrets Manager, `structlog` with a redaction processor, Alembic migrations, `pytest` + Faker for the eval set. |

**Evaluation harness:** build a labelled synthetic-resume set and track recall per entity type. Gate merges on a threshold (e.g. >= 98% recall on direct identifiers). We never say "guaranteed".

---

## 7. Data flow

```
Upload
  -> validate + malware scan + strip metadata/images
  -> encrypt (per-user DEK) -> S3
  -> parse text (in our infra, in-region)
  -> PII detect (Presidio, layered)
        |-- PII -> identity vault (encrypted)
        \-- redacted text (memory only)
  -> EGRESS GATEWAY: consent check + field allowlist + policy version
  -> LLM provider (redacted text only; model/prompt versions tagged)
  -> output PII re-scan
  -> analyses table (candidate_pid only)
  -> Student dashboard (own)  |  Recruiter (consent-gated pseudonymous card)
```

AI guardrails:
- Explain in the UI what the automated analysis does.
- Label the score as guidance: "not a hiring decision".
- Store `model_version`, `prompt_version` and `redaction_version` on every analysis.
- Trainer/human review path.
- Record what was sent to the LLM as a field list plus a hash, not the content.

---

## 8. Checklist mapping

| Area | Status |
|------|--------|
| Data inventory | Done in section 2 (needs the group's sign-off). |
| Consent & transparency | Drafted in the consent doc: screen, notice, purposes, retention, LLM disclosure, timestamp/version, withdrawal. |
| Security: HTTPS | Infra (Rahul): ALB + ACM, HSTS. |
| Security: auth, RBAC, backend authz | Hemanth + me. Role + batch scope + field allowlist in 2.4/2.5, enforced server-side (R6). OIDC with MFA for trainer/recruiter/admin proposed. |
| Security: encryption, file storage, secrets | Section 4. |
| Data lifecycle | Sections 5 and 7. |
| User rights (view/correct/delete/export/restrict) | Schema supports it (`dsr_requests`); endpoints in the next phase. |
| Accountability: consent logs, policy versioning | Schema in section 3, this phase. |
| Accountability: audit/access logs, breach procedure | Next phase (schema reserved). Breach: 72h to the authority, Art. 33. |
| AI | Section 7. |

---

## 9. Risks / things we're likely to neglect

- **R1. Wording.** "Anonymised" is inaccurate for a mapped pseudonym. Use "personal details removed".
- **R2. Consent may not be "freely given"** between students and their own institution (Recital 43) if placement access hinges on it. Purposes are recorded separately, so we can change the legal basis for core processing later. **[LEGAL]**
- **R3. Erasure vs backups vs consent proof.** Answer: crypto-shredding + `deletion_ledger` replay + minimal consent proof.
- **R4. PII detection is imperfect.** Residual leaks go to the LLM. Mitigations: layered detection, eval harness, known-user scrub, output scan, processor contract, and telling users not to include sensitive info.
- **R5. Recruiters become controllers** and we can't recall data. The notice must say so. Transfers to third countries need adequacy or SCCs. Art. 49 consent is an exceptional derogation, not for routine transfers. **[LEGAL]**
- **R6. Frontend RBAC is UX, not security.** Every API route enforces authorization server-side; RLS as a second layer.
- **R7. Secrets hygiene.** The feature branches have **no `.gitignore`** (it's only on `develop`). One committed `.env` or resume PDF stays in git history forever. Propose a `.gitignore` first on every branch (`.env`, `uploads/`, `*.pdf`, `*.docx`, keys) plus gitleaks.
- **R8. Graduation date.** Expiry depends on it. Missing date falls back to a hard cap.
- **R9. Latency (for Rahul).** Per-user KMS calls and Presidio NER add latency. Mitigations: short-TTL DEK caching, async redaction workers, models loaded once per worker, upload returns immediately.

---

## 10. Build order after sign-off

Steps 1-3 don't depend on the open items (region, countries/law, legal basis): region is config, the crypto sits behind `KeyProvider`, and the PII pipeline is region-agnostic. Only the final notice wording and the recruiter/transfer parts of consent wait on #4.

1. Schema + migrations (three zones), including batches, enrollments and trainer assignments; roles; RLS policies for batch scope.
2. Crypto module (envelope encryption, blind index) + tests.
3. PII pipeline + synthetic eval set/harness.
4. Consent service (API, append-only log, policy versions).
5. Egress gateway (consent + allowlist + version tagging).
6. Next phase: audit/access logs, DSR endpoints, retention/deletion jobs, breach procedure.
