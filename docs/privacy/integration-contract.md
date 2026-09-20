# Integration contract: auth ↔ privacy layer

**Between:** Hemanth (`api_server/`, `web_portal/`) and Shawn (`services/privacy/`)
**Status:** proposal, for Hemanth to agree or push back on | **Date:** 2026-09-20

The point of this document is that neither of us has to read the other's code
to stay compatible. There is one object that crosses the boundary and one rule
attached to it. Everything else is ours to change freely.

---

## 1. The boundary in one line

> **You prove *who* the caller is. I decide *what* they can see.**

| Concern | Owner |
|---|---|
| Login, tokens, sessions, password handling, MFA | Hemanth |
| Which role a user has | Hemanth |
| Which *rows* that role may read | Shawn (database-enforced) |
| Which *columns* a trainer may read | Shawn (database-enforced) |
| Encryption, redaction, consent, audit records | Shawn |
| Screens, routing, UX affordances | Hemanth |

Neither side needs the other's internals. You never write a `WHERE` clause for
scoping; I never verify a token.

---

## 2. What crosses: a `Principal`

```python
from pps_privacy.access import Principal

# AFTER you have verified the session/token:
principal = Principal.from_verified_auth(user_id, role)
```

**The one rule:**

> A `Principal` may only be built from *verified* authentication.
> Never from a header, query parameter, form field, or any other value the
> caller chooses.

This is enforced in code, not left to discipline. `from_verified_auth` will
refuse a malformed identifier and refuses outright to mint the privileged
`system` actor, whatever string it is handed.

---

## 3. What you get back

```python
from pps_privacy.access import resolve_scope, scoped_session

scope = resolve_scope(identity_conn, principal)      # once per request

with scoped_session(identity_conn, principal, scope) as session:
    rows = session.execute("SELECT user_id, name_enc FROM identity.users").fetchall()
```

That query returns the caller's own row, or their batch's students if they are
an assigned trainer, or nothing — **without any filtering in your code**. If a
route forgets to check something, it returns no rows rather than everyone's.

Scope settings are transaction-local, so nothing leaks between pooled
connections.

---

## 4. Four clashes to settle now

These are real differences between what is on `develop` today and what the
privacy layer expects. Each is cheap to fix now and expensive later.

### 4.1 User IDs must be UUIDs

Today: `stu_014`, `trn_007`, `adm_001`.
Needed: `uuid` (the `identity.users.user_id` column type).

Sequential IDs turn any weakness in authentication into impersonation of a
*chosen* person rather than a random one — guess `trn_007` and you are a
specific trainer. `Principal.from_verified_auth` rejects non-UUID identifiers
so the demo format cannot quietly become the production one.

### 4.2 Roles: five, not three

Today: `student`, `trainer`, `admin`.
Needed: those plus `recruiter` and `dpo`, matching the `users.role` CHECK
constraint. A role the database does not know fails at insert; a role I do not
know fails at `Principal` construction. They have to move together.

`system` is **not** a user role. It is the background-worker actor (retention
sweep, deletion worker) and must never be reachable from a request path.

### 4.3 Batch membership is many-to-many, and revocable

Today: `USERS[...]["batch"] = "PPS4027 A"` — one string per user.
Needed: the tables in migration 0002:

| Table | Why |
|---|---|
| `batch_enrollments(user_id, batch_id, status)` | A student can be in more than one batch over time |
| `trainer_assignments(trainer_id, batch_id, assigned_at, revoked_at)` | **`revoked_at` is the important column.** Access must end when teaching does, including for batches a trainer used to teach. A single string cannot express "used to" |
| `batches(..., graduation_date, trainer_identity_access)` | `graduation_date` drives the retention clock; the toggle lets a programme run trainers in pseudonymous-only mode |

### 4.4 Permission names promise scoping the code does not enforce

`view_assigned_students` and `review_assigned_submission` read as though they
are batch-scoped. `require_permission` only checks role → permission, so today
a trainer for Batch A passes the check for a student in Batch B.

**Keep the permission names.** They are good, and they map cleanly onto the
matrix in [phase1-notes.md](phase1-notes.md) section 2.4. What changes is that
the *data access* behind them goes through `scoped_session`, which supplies the
"assigned" part the names already promise.

Think of it as two separate questions:

- `require_permission("view_assigned_students")` → *may this role do this kind of thing at all?* Yours.
- `scoped_session(...)` → *which students, specifically?* Mine.

Both are needed. Neither replaces the other.

---

## 5. Wiring it up (FastAPI)

```python
from fastapi import Depends, HTTPException
from pps_privacy.access import Principal, PrincipalError, resolve_scope, scoped_session

def current_principal(session_user = Depends(verify_session)) -> Principal:
    """verify_session is yours: decode the token, check the signature/expiry.

    Only its *verified* output reaches Principal. Nothing from the raw request.
    """
    try:
        return Principal.from_verified_auth(session_user.id, session_user.role)
    except PrincipalError:
        raise HTTPException(status_code=401, detail="Invalid session")


@app.get("/api/students")
def list_students(
    principal: Principal = Depends(current_principal),
    _: dict = Depends(require_permission("view_assigned_students")),  # yours
):
    with get_identity_conn() as conn:
        scope = resolve_scope(conn, principal)
        with scoped_session(conn, principal, scope) as session:
            return session.execute(
                "SELECT user_id, name_enc FROM identity.trainer_student_view"
            ).fetchall()
```

Note `trainer_student_view` rather than the `users` table. The view is the
trainer field allowlist — name, student ID, institutional email, submission
status. Personal email and phone are **absent from it**, so there is no query
that returns them. You do not have to remember to exclude them.

---

## 6. One asymmetry worth knowing

Scoping works differently in the two data zones, and it will look inconsistent
until you know why:

- **Identity zone** (`identity.*`) — the database checks `trainer_assignments`
  itself. Scoping holds even if you pass an empty scope.
- **Analysis zone** (`analysis.*`) — this zone has no route to the identity
  schema by design, so it *cannot* check membership and relies on the resolved
  scope you pass in. Forget it and you see nothing (fails closed, as intended).

So: always call `resolve_scope` on an identity connection, then pass the result
to whichever connection needs it.

---

## 7. Things that must not happen

| Don't | Because |
|---|---|
| Build a `Principal` from request headers | That is today's auth bypass — the server believes whatever the caller claims |
| Let the frontend decide permissions | Frontend RBAC is UX. Anyone can call the API directly |
| Set `app.actor_role` yourself | Use `scoped_session`. Hand-set context outliving its transaction leaks scope between pooled requests |
| Let any input reach the `system` role | It is the one actor that sees every row |
| Log a decrypted name, email or resume | Use `RedactionResult.entity_counts` — counts, never values |
| Add `user_id` to an `analysis.*` table | It collapses the zone separation. There is a test that fails if you do |

---

## 8. Suggested order

1. **UUID identifiers** — touches the most code, blocks the rest, purely mechanical.
2. **Real sessions** — swap header trust for a signed token. This is the one that matters.
3. **Batch tables** — replace the `batch` string with enrollments and assignments.
4. **Route wiring** — `require_permission` + `scoped_session` together.
5. **Audit logging** — I will expose a helper; every trainer view of identity data
   has to land in `compliance.audit_log` (who, which student, which fields, when).

Steps 1 and 3 are safe to do now against the mock store. Step 2 is the real
work, and nothing else depends on it, so it does not have to block you.

---

## 9. Open questions for Hemanth

1. Which session mechanism — signed cookie, JWT, an OIDC provider? It changes
   nothing here, but it decides where `verify_session` gets its keys.
2. Does the frontend need a `dpo` view, or is that admin-console only for now?
3. Are the mock `USERS` entries worth keeping as seed data, once they carry
   UUIDs and real batch rows?
4. Who owns the login screen's consent step? The consent record has to be
   written before any resume is processed — see
   [consent-and-notice-draft.md](consent-and-notice-draft.md) section 3.
