from datetime import date

USERS = {
    "student": {
        "id": "stu_014",
        "name": "Aarav Mehta",
        "email": "aarav@example.edu",
        "role": "student",
        "batch": "PPS4027 A",
    },
    "trainer": {
        "id": "trn_007",
        "name": "Dr. Kavya Shah",
        "email": "kavya@example.edu",
        "role": "trainer",
        "batch": "PPS4027 A",
    },
    "admin": {
        "id": "adm_001",
        "name": "System Administrator",
        "email": "admin@example.edu",
        "role": "admin",
        "batch": "All batches",
    },
}

REPORT = {
    "submission_id": "sub_2026_014",
    "status": "Complete",
    "analysed_on": "19 Sep 2026, 11:20 AM",
    "ats_score": 76,
    "parseability": {
        "score": 88,
        "summary": "Text is readable; avoid a two-column layout for ATS exports.",
    },
    "keyword_match": {
        "score": 72,
        "summary": "Good alignment with the target role; add missing core terms.",
    },
    "section_structure": {
        "score": 68,
        "summary": "Most expected sections found; certifications needs a clearer heading.",
    },
    "detected_sections": [
        "Contact information",
        "Professional summary",
        "Education",
        "Skills",
        "Projects",
        "Experience",
    ],
    "skills": [
        "Python",
        "SQL",
        "Power BI",
        "Excel",
        "Communication",
    ],
    "matched_skills": [
        "Python",
        "SQL",
        "Power BI",
    ],
    "missing_skills": [
        "Data modelling",
        "Statistics",
        "ETL",
    ],
    "formatting_issues": [
        "Two font sizes appear in body text",
        "Contact details appear in the header",
    ],
    "recommendations": [
        "Use a single-column ATS-safe copy",
        "Add a Certifications heading",
        "Mention an ETL project in the summary",
    ],
}


def student_overview(student_id):
    if student_id != USERS["student"]["id"]:
        raise PermissionError("Student access required.")

    return {
        "active_module": "Module 1: Resume building",
        "completion": 62,
        "next_deadline": "CA1 resume review - 24 Sep",
        "reminders": [
            "Tuesday materials are available",
            "Join Wednesday Q&A at 4:00 PM",
            "Submit CA1 before the deadline",
        ],
    }


def content_library():
    return [
        {
            "week": "Week 1",
            "module": "Resume building",
            "title": "ATS-ready resume basics",
            "type": "Reading + worksheet",
            "released": True,
        },
        {
            "week": "Week 2",
            "module": "Resume building",
            "title": "Tailoring a resume to a JD",
            "type": "Video + practice",
            "released": True,
        },
        {
            "week": "Week 3",
            "module": "Resume building",
            "title": "Writing impact-focused projects",
            "type": "Reading",
            "released": False,
        },
    ]


def calendar_events():
    return [
        {
            "date": "22 Sep",
            "event": "Tuesday content drop",
            "location": "Content library",
        },
        {
            "date": "23 Sep",
            "event": "Live Q&A",
            "location": "MS Teams",
        },
        {
            "date": "24 Sep",
            "event": "CA1 resume review due",
            "location": "Assignment area",
        },
        {
            "date": "25 Sep",
            "event": "Weekly MCQ",
            "location": "MS Forms",
        },
    ]


def assignments(student_id):
    if student_id != USERS["student"]["id"]:
        raise PermissionError("Student access required.")

    return [
        {
            "assessment": "CA1",
            "title": "Resume review",
            "due": "24 Sep",
            "status": "Complete",
            "score": "76 / 100",
        },
        {
            "assessment": "CA2",
            "title": "Group discussion",
            "due": "16 Oct",
            "status": "Not open",
            "score": "-",
        },
        {
            "assessment": "CA3",
            "title": "Personal interview",
            "due": "30 Oct",
            "status": "Not open",
            "score": "-",
        },
    ]


def get_report(actor, submission_id):
    allowed = (
        actor["role"] == "admin"
        or (
            actor["role"] == "student"
            and actor["id"] == USERS["student"]["id"]
        )
        or (
            actor["role"] == "trainer"
            and actor["batch"] == USERS["trainer"]["batch"]
        )
    )

    if not allowed or submission_id != REPORT["submission_id"]:
        raise PermissionError("Not allowed to view this report.")

    return REPORT


def submit_resume(actor, filename, jd):
    if (
        actor["role"] != "student"
        or actor["id"] != USERS["student"]["id"]
    ):
        raise PermissionError("Only the owner can create a submission.")

    return {
        "submission_id": REPORT["submission_id"],
        "status": "Queued",
        "filename": filename,
        "has_target_jd": bool(jd.strip()),
    }


def trainer_submissions(actor):
    if actor["role"] not in {"trainer", "admin"}:
        raise PermissionError("Trainer access required.")

    return [
        {
            "student": "Aarav Mehta",
            "assessment": "CA1",
            "status": "Complete",
            "ats_score": 76,
            "review": "Needs review",
        },
        {
            "student": "Nisha Rao",
            "assessment": "CA1",
            "status": "Processing",
            "ats_score": None,
            "review": "Waiting",
        },
        {
            "student": "Sana Ali",
            "assessment": "CA1",
            "status": "Submitted",
            "ats_score": None,
            "review": "Waiting",
        },
    ]


def audit_events(actor):
    if actor["role"] != "admin":
        raise PermissionError("Admin access required.")

    return [
        {
            "time": "19 Sep, 11:20",
            "event": "ATS report viewed",
            "actor": "Aarav Mehta",
            "result": "Allowed",
        },
        {
            "time": "19 Sep, 11:18",
            "event": "Resume analysis completed",
            "actor": "System",
            "result": "Success",
        },
        {
            "time": "19 Sep, 10:55",
            "event": "Consent recorded",
            "actor": "Aarav Mehta",
            "result": "Success",
        },
    ]


def system_configuration():
    return {
        "max_upload_mb": 5,
        "retention_days": 180,
        "ats_weights": {
            "Parseability": 40,
            "Keyword match": 40,
            "Section structure": 20,
        },
        "last_updated": date.today().isoformat(),
    }


def authenticate(account_key: str, claimed_role: str) -> dict:
    """
    Simulate a backend authentication + RBAC authorisation check.

    In production this would verify credentials against the identity service
    and compare the account's assigned role with the role being claimed.
    Here it mirrors that logic against the mock user store.

    Parameters
    ----------
    account_key   : key into USERS dict (e.g. "student", "trainer", "admin")
    claimed_role  : role string the login form is asserting (e.g. "student")

    Returns
    -------
    dict  — the matched USERS entry

    Raises
    ------
    KeyError        — account_key not found in USERS
    PermissionError — account exists but its role ≠ claimed_role
    """
    user = USERS.get(account_key)

    if user is None:
        raise KeyError(f"No demo account found for key '{account_key}'.")

    if user["role"] != claimed_role:
        raise PermissionError(
            f"Account '{user['name']}' is registered as "
            f"'{user['role']}', not '{claimed_role}'. "
            "Access denied."
        )

    return user