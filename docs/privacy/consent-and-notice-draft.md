# Consent form & privacy notice - DRAFT v0.1

**Owner:** Shawn | **Status:** for team review | **Date:** 2026-09-19
Placeholders in `[BRACKETS]` need real values. **[LEGAL]** review is required before this goes live. This is not legal advice.

---

## 1. Design rules (GDPR Art. 7, Recitals 32/42/43)

- **Opt-in only:** nothing pre-ticked, no bulk "accept all" as the only path.
- **Granular:** one purpose per checkbox, not bundled with terms of service.
- **Plain language:** say what, why, who, how long, in one or two sentences, with details expandable.
- **Freely given:** only purposes 1-2 are required, and only for the resume feature. Declining 3-6 never blocks the dashboard or resume analysis.
- **Withdraw as easily as given:** one toggle in Privacy & Data, effective immediately.
- **Provable:** every choice stores who, what, which text version, and when.
- **Versioned:** any material change to purposes or recipients means a new version and a fresh consent.

## 2. Purposes

| Code | Shown as | Required? | If declined |
|------|----------|-----------|-------------|
| `resume_analysis` | Analyse my resume | To use resume analysis only | Resume features unavailable |
| `ai_processing` | Use an AI service (personal details removed first) | To use AI-based analysis | AI features unavailable [open: rules-only fallback?] |
| `recruiter_visibility` | Show my profile to recruiters, without name or contact details | No | Not listed |
| `recruiter_reveal` | Let recruiters request my contact details. I approve each request. | No | Requests blocked |
| `intl_transfer` | Allow recruiters outside [REGION] to see my profile | No | Only recruiters inside [REGION] |
| `alumni_retention` | Keep my data [12] months after graduation | No | Standard expiry applies |

`recruiter_reveal` is also asked again per request: "[Recruiter] from [Company] ([Country]) asks for your contact details", with allow/deny and an expiry.

## 3. Consent screen wireframe

```
+--------------------------------------------------------------------+
|  Your data, your choice                                  Notice v1.0|
|--------------------------------------------------------------------|
|  Before you upload a resume, tell us what we may do with it.       |
|  Nothing is ticked. You can change any choice later in             |
|  Privacy & Data.                                                   |
|                                                                    |
|  NEEDED TO ANALYSE YOUR RESUME                                     |
|  [ ] 1. Analyse my resume                                          |
|         We read it to find skills, gaps and tips. Kept until       |
|         [6] months after you graduate.                [Details v]  |
|  [ ] 2. Use an AI service                                          |
|         Your resume text, with your name, email, phone, address    |
|         and links removed, is sent to [PROVIDER] ([REGION]).       |
|         They may not keep it or train on it.          [Details v]  |
|                                                                    |
|  OPTIONAL - saying no does not affect 1 and 2                      |
|  [ ] 3. Show my profile to recruiters (no name or contact)         |
|  [ ] 4. Let recruiters ask for my contact details                  |
|         You approve or refuse each request.                        |
|  [ ] 5. Allow recruiters outside [REGION] to see my profile        |
|         Their country may have weaker data-protection rules.      |
|         [What this means v]                                        |
|  [ ] 6. Keep my data [12] months after graduation                  |
|                                                                    |
|  Read the full privacy notice (v1.0)                               |
|                                                                    |
|            [ Save my choices ]        [ Not now ]                  |
+--------------------------------------------------------------------+
```

## 4. "Privacy & Data" page wireframe (withdrawal + rights)

```
+--------------------------------------------------------------------+
|  Privacy & Data                                                    |
|--------------------------------------------------------------------|
|  MY CHOICES                              Given on        Change    |
|  Analyse my resume                       2026-09-21      [ON  ]    |
|  Use an AI service                       2026-09-21      [ON  ]    |
|  Show my profile to recruiters           -               [OFF ]    |
|  ...                                                               |
|                                                                    |
|  MY DATA                                                           |
|  [ View what you hold about me ]  [ Download my data (ZIP/JSON) ]  |
|  [ Correct my details ]           [ Pause processing ]             |
|  [ Delete my resume ]             [ Delete my account + all data ] |
|                                                                    |
|  WHO SAW MY DATA                                                   |
|  2026-09-25  Recruiter X (Company Y, DE) - contact details         |
|                                                                    |
|  Questions or complaints: [DPO EMAIL]                              |
+--------------------------------------------------------------------+
```

## 5. What happens on withdrawal

| Withdrawn | Effect |
|-----------|--------|
| `resume_analysis` | In-flight jobs cancelled. Resume file and analysis deleted (job within 24 h). |
| `ai_processing` | No new external AI calls. Existing analysis stays unless the user deletes it. |
| `recruiter_visibility` | Profile removed from recruiter search immediately. Data a recruiter already received can't be recalled. We say so in the notice. |
| `recruiter_reveal` | Future requests blocked. Past reveals stay in the access history. |
| `intl_transfer` | Profile hidden from recruiters outside [REGION]. |
| `alumni_retention` | Standard graduation-based expiry applies from the original date. |

## 6. Consent record model

```
consent_records   -- append-only: INSERT only, no UPDATE/DELETE grants
  consent_id      uuid PK
  subject_pid     uuid          -- pseudonymous ref, not user_id
  purpose_code    text
  action          text          -- granted | withdrawn
  scope           jsonb         -- e.g. {recruiter_id, expires_at} for per-request reveals
  policy_version  text          -- notice version shown
  notice_hash     text          -- sha256 of the exact text rendered
  ui_version      text
  occurred_at     timestamptz   -- UTC, server clock
  ip_hash         text          -- optional HMAC(IP): proof without storing the raw IP
```

Current state = latest row per (`subject_pid`, `purpose_code`, `scope`). Withdrawing appends a row; nothing is edited or deleted. These records survive erasure of the rest of the user's data (minimal proof, Art. 17(3)(e)) **[LEGAL: how long]**.

## 7. Privacy notice draft (Art. 13)

**Version 0.1 - [DATE]**

**1. Who we are.** [ORG NAME] ("we") runs [PLATFORM] and decides why and how your data is used. Contact: [EMAIL]. Data Protection Officer: [DPO NAME/EMAIL].

**2. What we collect.**
- *Account:* name, email, graduation date, programme (phone optional).
- *Your resume:* the file you upload and what we derive from it (skills, scores, issues, recommendations).
- *Technical:* login events, IP address, timestamps, for security and to show you who accessed your data.
- *What we deliberately don't keep:* photos, date of birth, gender, marital status, nationality, religion, government IDs, and referees' details. If your resume has them, we remove them automatically. Please leave them out.

**3. Why we use it, and on what basis.**

| Purpose | Basis |
|---------|-------|
| Analyse your resume and give feedback | Your consent (Art. 6(1)(a)) [LEGAL] |
| Process with an AI service (details removed first) | Your consent |
| Show your profile to recruiters | Your consent |
| Share your contact details with a recruiter you approve | Your consent, per request |
| Security, fraud prevention, audit logs | Legitimate interests |

**4. Who receives it.**

| Recipient | What they get | Why |
|-----------|---------------|-----|
| [CLOUD PROVIDER], [REGION] | Encrypted data | Hosting (processor) |
| [AI PROVIDER], [REGION] | Resume text with name, contact details and links removed | Analysis (processor); they may not keep it or train on it |
| Recruiters you allow | Your profile without name or contact details. Contact details only if you approve. | Recruiting. **They become responsible for their own copy** and we can't take it back. |

**5. Transfers outside [REGION].** Only if you consent to it (choice 5) or an adequacy decision / Standard Contractual Clauses apply. **[LEGAL]** Tell users the risks: the recipient's country may not offer equivalent protection.

**6. How long we keep it.** Until [6] months after your graduation date, or [12] if you opt into extended retention, or sooner if you delete it or withdraw consent. Backups are cleared within [35] days. Consent records are kept [N] years as proof.

**7. Automated analysis.** An algorithm scores your resume for structure, skills and ATS-compatibility. **It is guidance for you, not a hiring decision.** No decision about you with legal or similarly significant effect is made solely by automated means. [Trainer/human review: describe]. We record which model version produced each analysis.

**8. Your rights.** Access, correction, deletion, export, restriction, objection, withdrawing consent at any time (without affecting earlier processing). Use Privacy & Data or email [EMAIL]; we respond within one month.

**9. Security.** Encryption in transit and at rest, role-based access, audit logging, regional storage in [REGION].

**10. Changes.** If we change purposes or recipients, we publish a new version and ask again. Old versions are archived.

**11. Complaints.** You can complain to your data-protection authority: [AUTHORITY, CONTACT].

## 8. Open points for the team

1. If a student declines `ai_processing`, do we offer a rules-only fallback, or is the feature simply unavailable?
2. Grace period after graduation (6 months proposed).
3. Consent-proof retention period **[LEGAL]**.
4. Languages the notice and consent screen must ship in.
5. Are any students under 18? If so we need age handling and parental consent rules per country.
6. DPO name/contact and the supervisory authority to name in the notice.
