from datetime import date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Mock User Store
USERS: Dict[str, Dict[str, Any]] = {
    "student": {
        "id": "stu_014",
        "name": "Aarav Mehta",
        "email": "aarav@example.edu",
        "role": "student",
        "batch": "PPS4027 A",
        "roll_no": "PPS-2024-4027",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        "cohort": "Cohort AY 2024–25 · Week 4",
        "track": "Data & Analytics Track"
    },
    "trainer": {
        "id": "trn_007",
        "name": "Dr. Kavya Shah",
        "email": "kavya@example.edu",
        "role": "trainer",
        "batch": "PPS4027 A",
        "title": "Lead Faculty & Evaluator",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        "cohort": "Batch 2025 · Cohort B",
        "track": "Vocational Evaluator Desk"
    },
    "admin": {
        "id": "adm_001",
        "name": "Prof. K. V. Ramanathan",
        "email": "admin@example.edu",
        "role": "admin",
        "batch": "All batches",
        "title": "Program Administrator & Dean",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        "cohort": "Institution Registry",
        "track": "Academic Governance"
    },
}

# Role permissions map
ROLE_PERMISSIONS: Dict[str, set] = {
    "student": {
        "view_own_profile",
        "submit_resume",
        "view_own_report",
        "manage_own_privacy",
        "view_courseware",
    },
    "trainer": {
        "view_assigned_students",
        "view_assigned_reports",
        "review_assigned_submission",
        "publish_grades",
    },
    "admin": {
        "manage_users",
        "manage_configuration",
        "view_audit_log",
        "export_forensic_trail",
    },
}

DEFAULT_REPORT = {
    "submission_id": "sub_2026_014",
    "student_name": "Aarav Mehta",
    "student_id": "stu_014",
    "status": "Complete",
    "analysed_on": "19 Sep 2026, 11:20 AM",
    "ats_score": 76,
    "grade": "B+ (Distinction Track)",
    "filename": "Aarav_Mehta_Resume_v2.4.pdf",
    "target_role": "Thoughtworks · Graduate Data Analyst",
    "parseability": {
        "score": 88,
        "summary": "Single-column layout parsed cleanly. Text layer extractable with zero unicode errors.",
        "details": [
            "Standard UTF-8 character encoding verified",
            "Heading hierarchy recognized by parsers",
            "No non-standard text boxes or embedded tables detected"
        ]
    },
    "keyword_match": {
        "score": 72,
        "summary": "Solid alignment with Graduate Data Analyst competencies; add missing core terms.",
        "details": [
            "Strong density on Python, SQL, and Power BI",
            "Missing critical keywords: Data Modelling, Statistics, ETL",
            "Add quantifiable action verbs to experience bullet points"
        ]
    },
    "section_structure": {
        "score": 68,
        "summary": "Most expected sections found; clarify Certifications and Leadership headings.",
        "details": [
            "Education, Skills, Experience, and Projects clearly isolated",
            "Missing dedicated 'Certifications' section header",
            "Contact information positioned correctly in body header"
        ]
    },
    "detected_sections": [
        "Contact Information",
        "Professional Summary",
        "Education",
        "Technical Skills",
        "Projects & Practicums",
        "Internship Experience",
    ],
    "skills": [
        "Python",
        "SQL",
        "Power BI",
        "Excel",
        "Communication",
        "Data Cleaning",
        "Git",
        "Pandas"
    ],
    "matched_skills": [
        "Python",
        "SQL",
        "Power BI",
        "Excel",
        "Data Cleaning"
    ],
    "missing_skills": [
        "Data Modelling",
        "Inferential Statistics",
        "ETL Pipelines",
        "Cloud Basics (AWS/GCP)"
    ],
    "formatting_issues": [
        "Two distinct font sizes detected in body description bullets",
        "Contact icons used without accompanying plain-text labels"
    ],
    "recommendations": [
        "Use a single-column ATS-safe format without multi-column margins",
        "Add a dedicated 'Certifications & Accreditations' section heading",
        "Mention at least one end-to-end ETL pipeline project with metrics in summary",
        "Quantify project achievements with percentages or turnaround improvements"
    ],
    "trainer_feedback": "Good structural foundation, Aarav. Enhance the analytics metrics in your project descriptions before CA1 locks."
}

SUBMISSIONS_DB = [
    {
        "id": "sub_2026_014",
        "student": "Aarav Mehta",
        "student_id": "stu_014",
        "roll_no": "PPS-2024-4027",
        "filename": "Aarav_Mehta_Resume_v2.4.pdf",
        "target_role": "Thoughtworks · Graduate Data Analyst",
        "assessment": "CA1",
        "submitted_date": "19 Sep 2026, 11:20 AM",
        "status": "Complete",
        "ats_score": 76,
        "review_status": "Needs review",
        "trainer_notes": "Draft ready for final sign-off.",
        "batch": "PPS4027 A"
    },
    {
        "id": "sub_2026_015",
        "student": "Nisha Rao",
        "student_id": "stu_015",
        "roll_no": "PPS-2024-4028",
        "filename": "Nisha_Rao_CV_Tech.pdf",
        "target_role": "TCS · Associate Software Engineer",
        "assessment": "CA1",
        "submitted_date": "19 Sep 2026, 10:15 AM",
        "status": "Processing",
        "ats_score": 82,
        "review_status": "Waiting",
        "trainer_notes": "Awaiting automated parsing worker.",
        "batch": "PPS4027 A"
    },
    {
        "id": "sub_2026_016",
        "student": "Sana Ali",
        "student_id": "stu_016",
        "roll_no": "PPS-2024-4029",
        "filename": "Sana_Ali_Product_Resume.pdf",
        "target_role": "Deloitte · Business Tech Analyst",
        "assessment": "CA1",
        "submitted_date": "18 Sep 2026, 04:45 PM",
        "status": "Submitted",
        "ats_score": 69,
        "review_status": "Waiting",
        "trainer_notes": "Initial submission received.",
        "batch": "PPS4027 A"
    }
]

AUDIT_DB = [
    {
        "time": "19 Sep, 11:20",
        "event": "ATS report viewed",
        "actor": "Aarav Mehta (stu_014)",
        "result": "Allowed",
        "category": "Assessment"
    },
    {
        "time": "19 Sep, 11:18",
        "event": "Resume analysis completed",
        "actor": "System Engine v4.2",
        "result": "Success",
        "category": "Ingestion"
    },
    {
        "time": "19 Sep, 10:55",
        "event": "Consent recorded",
        "actor": "Aarav Mehta (stu_014)",
        "result": "Success",
        "category": "Compliance"
    }
]

SYSTEM_CONFIG_DB = {
    "max_upload_mb": 5,
    "retention_days": 180,
    "ats_weights": {
        "parseability": 40,
        "keyword_match": 40,
        "section_structure": 20
    },
    "last_updated": date.today().isoformat(),
    "engine_version": "v4.2.8-production"
}
