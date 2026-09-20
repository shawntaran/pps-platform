# Infrastructure, residency, LLM provider & latency — findings

**Owner:** Shawn | **Branch:** `feature/privacy-layer` | **Status:** DRAFT, covering the items parked pending Rahul | **Date:** 2026-09-20

Covers open decisions #1 (region / LLM provider) and #6 (encryption mechanism) from
[phase1-notes.md](phase1-notes.md), plus a first pass at the latency brief that is Rahul's focus.

> Written without Rahul. Everything here is a **proposal with reasoning**, not a decision taken over him.
> Section 7 lists exactly what he should overrule if he disagrees.
> Items marked **[VERIFY]** I could not confirm and must be checked against live docs before we build on them.

---

## 1. The reframing that makes the rest of this easy

"Localized server data storage" bundles three different questions that have three different answers:

| Question | What it governs | Answer |
|---|---|---|
| Where does data **rest**? | RDS, S3, backups, KMS keys | ap-south-1. Straightforward, cheap, do it. |
| Where is data **processed** by us? | App servers, Presidio workers | Same region. Falls out of the above. |
| Where is data **processed by a third party**? | The LLM call | **The redaction layer is the answer, not the region.** |

The third row is the important one. We spent Phase 1 building a pipeline whose entire purpose is that
**the text leaving our boundary carries no direct identifiers**. If that works, the LLM call is not a
transfer of identifiable personal data, and the residency bar for the provider drops sharply.

If it does not work, no amount of region-pinning saves us — we would be shipping PII abroad with
extra steps. So the redaction eval harness (notes §6) is load-bearing for this decision, not a nice-to-have.
**Region choice is a second line of defence behind redaction, not a substitute for it.**

---

## 2. Is localization actually required? (This is not what the brief assumed)

The brief says "localized server data storage" and "full GDPR compliance for international recruiting".
Two corrections, both of which need **[LEGAL]** sign-off:

**a) India's DPDP Act does not broadly mandate data localization.** Unlike the RBI's payment-data rules,
the DPDP Act 2023 permits cross-border transfer except to countries the government restricts
(a blacklist model, not a whitelist). So storing in India is a **defensible choice** — better latency,
a cleaner story for students and institutions, simpler audit — but as far as I can tell it is not the
legal mandate the brief implies. **[VERIFY]** — my knowledge runs to roughly May 2026 and the DPDP Rules
were still being phased in; someone must check the current notified position.

**b) GDPR may not govern student data at all.** GDPR Art. 3(2) reaches data subjects *in the Union*.
If every student is in India, their data is governed by DPDP, not GDPR. GDPR would apply to the
**recruiter** contacts who are in the EU, and to us as a matter of posture.

This matters more than it sounds, because **DPDP has no "legitimate interests" basis.** Its
§7 "legitimate uses" are a narrow enumerated list, with no GDPR-style balancing test.

> **This partly walks back my trainer-access recommendation.** In the notes I argued trainer review should
> run on *contract / legitimate interest* rather than consent. That reasoning is sound **under GDPR**.
> Under DPDP the nearest ground is "the specified purpose for which the Data Principal voluntarily
> provided her personal data" — arguably fine for a student who enrols and submits a resume for review,
> but it is a different argument and it needs checking. My conclusion (don't fake a consent checkbox
> for something a student cannot refuse) still holds; the legal route to it changes. **[LEGAL]**

**Recommendation:** build to whichever standard is stricter per control, and stop describing the target
as "GDPR compliance". Call it "DPDP compliant, GDPR-aligned". It is more accurate and it is a better
line for recruiters.

---

## 3. Decision R1 — storage region

**Proposal: `ap-south-1` (Mumbai).** Single region, no multi-region replication in Phase 1.

- Closest mature AWS region to the users; every service we need (RDS, S3, KMS, Secrets Manager) is there.
- `ap-south-2` (Hyderabad) is newer with thinner service coverage — not worth a second region we do not
  yet need. **[VERIFY]** current service parity if anyone prefers it.
- **KMS keys stay single-region.** Do *not* create multi-region keys: a multi-region key replica is a
  copy of the key material in another jurisdiction, which quietly undoes the residency story.
- **Backups and read replicas must be pinned to the same region.** Easy to get wrong later when someone
  enables cross-region snapshot copy for DR. Put it in the infra review checklist.

**The thing region does not buy us.** An EU recruiter logging in and viewing a candidate card is a
cross-border *access* regardless of where the database sits. Residency controls where bytes rest; it
does nothing about who reads them from where. That stays a consent + contract problem
(`intl_transfer` purpose, notes §R5).

---

## 4. Decision R2 — LLM provider

### What we need

No training on our data; no or short retention; a DPA; inference we can locate; and ideally not a new
processor relationship on top of the AWS one we already need.

### What I found (and what changed my mind)

I started out assuming the first-party Claude API with its `inference_geo` residency parameter, plus the
Batch API for the 50% discount. Checking the availability table killed both assumptions:

| Capability | First-party API | Amazon Bedrock |
|---|---|---|
| `inference_geo` (residency pin) | Yes — but **only accepts `us` / `global`** | **Not supported** |
| Message Batches (50% cost) | Yes | **Not supported** |
| Prompt caching | Yes | Yes |
| Runs inside our own AWS account / VPC | No | Yes (PrivateLink) |

So `inference_geo` is useless to us either way — there is no India or EU value, only `us`/`global`.
**The only way to keep inference in India is Bedrock in `ap-south-1`**, where the region *is* the control.

### Proposal: Amazon Bedrock in `ap-south-1`

- Inference stays in-region; no new processor — it is the AWS DPA we already need for RDS/S3/KMS.
- A VPC endpoint (PrivateLink) means redacted text never crosses the public internet.
- CloudTrail already gives us the audit trail.
- Bedrock does not use customer inference data to train models. **[VERIFY]** against current AWS terms.

### The trap: cross-region inference profiles

Bedrock increasingly serves newer models through **inference profiles that spread requests across several
regions in a geography** for capacity. If we call an APAC profile rather than a region-pinned model, our
"data stays in India" claim silently becomes false — and nothing in our code would show it.

**[VERIFY] before committing:** which Claude models are available in `ap-south-1` as *region-pinned*
invocations rather than only via a multi-region profile. If the models we want are profile-only, this
recommendation weakens and we should reopen the first-party option.

This is exactly the class of thing Rahul was asked to catch, so it is his call to make with real data.

### Cost is not a decision driver here

Rough per-analysis cost at ~3K input / ~1.5K output tokens (first-party list prices; Bedrock is priced
separately **[VERIFY]**):

| Model | $/MTok in/out | ≈ per resume | 2,000 analyses |
|---|---|---|---|
| `claude-opus-5` | $5 / $25 | ~$0.05 | ~$100 |
| `claude-sonnet-5` | $2 / $10 | ~$0.02 | ~$40 |
| `claude-haiku-4-5` | $1 / $5 | ~$0.01 | ~$20 |

At student-cohort scale the spread is tens of dollars. **Losing the Batch discount by choosing Bedrock
costs less than the time we would spend arguing about it** — so decide on compliance and latency, not
price. I would start on `claude-opus-5` for analysis quality and measure whether `claude-sonnet-5` holds
up on our eval set before trading down; that is a quality decision for the lead, not a cost decision for me.

### Fallback for students who decline AI processing

Open question 1 in the consent draft. A small **rules-only analyser** we host (keyword and skills
matching, structure and formatting checks, no LLM) answers it: those students still get useful ATS
feedback, their data never leaves our infrastructure, and the consent becomes genuinely free because
refusing costs them something small rather than everything. Worth scoping.

---

## 5. Decision R3 — the "already established" encryption mechanism

Still unconfirmed by Rahul, so I am specifying what we build to. Nothing blocks on him, because it sits
behind an interface:

```
KeyProvider (interface)
  |-- KmsKeyProvider    -> AWS KMS, ap-south-1, per-data-class CMK   [prod]
  \-- LocalKeyProvider  -> key from env/file, dev and tests only     [dev]
```

| Layer | Choice |
|---|---|
| File + field encryption | AES-256-GCM, per-user data key, AAD bound to table+column+user_id |
| Key wrapping | KMS envelope encryption, CMK per data class, single-region, auto-rotation on |
| Erasure | Destroy the per-user DEK (crypto-shredding) — reaches backups too |
| Transport | TLS 1.2+ everywhere; `sslmode=verify-full` to Postgres |
| Library | Python `cryptography` (AES-GCM) or the AWS Encryption SDK. **Never shell out to the `openssl` CLI** |
| Secrets | AWS Secrets Manager. Never in git. `gitleaks` pre-commit |

If Rahul's established mechanism differs, we swap the `KeyProvider` implementation and nothing else
moves. That is the point of the interface.

---

## 6. Latency — first pass at Rahul's brief

### The single most important decision

**Uploads must return immediately.** The user gets a job ID and a progress state; analysis runs on a
worker queue. Once that is true, the LLM's multi-second latency stops being a UX problem and almost
everything below becomes a throughput question instead of a latency question.

If we ever let the request thread wait for the full pipeline, nothing else in this section will save us.

### Where the privacy layer genuinely adds cost

| Stage | Cost | Mitigation |
|---|---|---|
| Model load (spaCy/Presidio) | **Seconds** — catastrophic if per-request | Load once per worker at startup; warm pool; never lazy-load in a handler |
| PII detection | CPU-bound, scales with document length | Run once, cache the redacted text for the job's lifetime; try `en_core_web_lg` before reaching for a transformer |
| KMS calls | ~10–50ms each, and **per-region request quotas** | Cache the plaintext DEK in memory with a short TTL; watch for N+1 calls in list views |
| Output PII rescan | Small — LLM output is short | Keep it. Cheap insurance |
| LLM call | **Dominant**, seconds | Async. Prompt caching on the stable system prompt. Hard timeout, bounded retries |

**The DEK cache is a real tradeoff, not a free win.** A cached plaintext key is a key sitting in process
memory. Bound the TTL, never log it, zeroise on eviction, keep it out of crash dumps. Worth discussing
with Rahul rather than me deciding.

### Traps I would bet on us hitting

1. **Per-request model loading** — turns a 200ms redaction into a 5s one. The classic.
2. **N+1 KMS decrypts** — a trainer's list of 40 students triggering 40 `Decrypt` calls. Batch or cache.
3. **No timeout on the LLM call** — one hung request holds a worker forever.
4. **Retries amplifying an outage** — backoff and a cap, or a provider blip becomes our outage.
5. **Synchronous malware scanning / PDF parsing** blocking the event loop on a 10MB file.
6. **Cold starts** if anyone reaches for Lambda for the Presidio workers — model load makes that a bad fit.
7. **Logging the thing we redacted.** A debug log of the pre-redaction text defeats the entire layer.
   This is a privacy bug wearing a latency bug's clothes, and it will be added by someone debugging latency.

### What to measure

p50/p95 per stage, not end-to-end only — an end-to-end number hides which stage regressed. Set a budget
per stage once we have real numbers. I have deliberately not invented target milliseconds; Rahul should
set them against measurements.

---

## 7. What Rahul should overrule

| # | I proposed | Overrule if |
|---|---|---|
| 1 | `ap-south-1`, single region | Users are concentrated elsewhere, or DR policy needs a second region |
| 2 | Bedrock `ap-south-1` over first-party API | The models we need are served only via multi-region profiles, or he wants the Batch discount |
| 3 | AES-256-GCM + KMS envelope, per-user DEK | The established mechanism differs — swap `KeyProvider`, nothing else changes |
| 4 | Short-TTL DEK cache | He judges the in-memory key exposure not worth the latency saving |
| 5 | Async job queue for all analysis | — I would push back hard on this one |

## 8. Verification checklist before any of this is built

- [ ] Claude model availability in `ap-south-1`, **region-pinned vs inference-profile only** — blocks §4
- [ ] Current Bedrock terms on training and retention of inference data
- [ ] Bedrock `ap-south-1` pricing (differs from the first-party list prices quoted above)
- [ ] DPDP Rules: current notified status, and whether any localization duty applies to us
- [ ] Whether GDPR applies to student data at all, or only to EU recruiter contacts **[LEGAL]**
- [ ] Legal basis for trainer review **under DPDP**, given there is no legitimate-interests ground **[LEGAL]**
- [ ] `ap-south-2` service parity, if anyone prefers Hyderabad
