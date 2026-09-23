from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import random

from api_server.database import USERS, DEFAULT_REPORT, SUBMISSIONS_DB, AUDIT_DB, SYSTEM_CONFIG_DB
from api_server.security import authenticate_user, require_auth, require_permission

app = FastAPI(
    title="PPS4027 Placement Portal Backend API",
    description="Server-enforced RBAC & continuous assessment processing engine",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite port 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class LoginRequest(BaseModel):
    account_key: str
    claimed_role: str

class SubmitResumeRequest(BaseModel):
    filename: str
    target_role: str
    target_jd: str

class ReviewSubmissionRequest(BaseModel):
    submission_id: str
    review_status: str
    feedback_notes: str
    adjusted_score: Optional[int] = None

class SystemConfigRequest(BaseModel):
    retention_days: int
    ats_weights: Dict[str, int]

# Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PPS4027 Placement API",
        "engine": "v4.2.8-production",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/login")
def login_endpoint(payload: LoginRequest):
    """
    Validate demo login role against backend USERS database.
    Rejects mismatched role claims with 403 Forbidden.
    """
    user = authenticate_user(payload.account_key, payload.claimed_role)
    
    # Record audit log
    AUDIT_DB.insert(0, {
        "time": datetime.now().strftime("%d %b, %H:%M"),
        "event": f"Authenticated session started ({user['role'].upper()})",
        "actor": f"{user['name']} ({user['id']})",
        "result": "Success",
        "category": "Auth"
    })
    
    return {
        "success": True,
        "user": user,
        "token": f"token_{user['id']}_{user['role']}"
    }

# Student Protected Endpoints
@app.get("/api/student/overview")
def student_overview(user: Dict[str, Any] = Depends(require_permission("view_own_profile"))):
    return {
        "student_id": user["id"],
        "name": user["name"],
        "active_module": "Module 1: Resume Building & ATS Calibration",
        "completion_percentage": 62,
        "next_deadline": "CA1 Single-Column Resume - 24 Sep 2026, 11:59 PM",
        "reminders": [
            "Tuesday content drops are available in Content Library",
            "Join Wednesday Live Q&A w/ Faculty at 4:00 PM IST",
            "Submit CA1 single-column CV before lock"
        ]
    }

@app.get("/api/student/report/{submission_id}")
def get_diagnostic_report(
    submission_id: str,
    user: Dict[str, Any] = Depends(require_auth)
):
    """
    Enforces that students can only view their own reports,
    while trainers and admins can inspect cohort reports.
    """
    if user["role"] == "student" and user["id"] != DEFAULT_REPORT["student_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You cannot view reports belonging to other students."
        )
    return DEFAULT_REPORT

@app.post("/api/student/submit-resume")
def submit_resume_endpoint(
    payload: SubmitResumeRequest,
    user: Dict[str, Any] = Depends(require_permission("submit_resume"))
):
    base_score = random.randint(75, 90)
    sub_id = f"sub_2026_{random.randint(100, 999)}"
    
    new_sub = {
        "id": sub_id,
        "student": user["name"],
        "student_id": user["id"],
        "roll_no": user.get("roll_no", "PPS-2024-4027"),
        "filename": payload.filename,
        "target_role": payload.target_role,
        "assessment": "CA1",
        "submitted_date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "status": "Complete",
        "ats_score": base_score,
        "review_status": "Needs review",
        "trainer_notes": "Awaiting mentor evaluation.",
        "batch": user.get("batch", "PPS4027 A")
    }
    
    SUBMISSIONS_DB.insert(0, new_sub)
    
    AUDIT_DB.insert(0, {
        "time": datetime.now().strftime("%d %b, %H:%M"),
        "event": f"Resume submitted and ATS analyzed ({payload.filename})",
        "actor": f"{user['name']} ({user['id']})",
        "result": "Success",
        "category": "Assessment"
    })

    return {
        "submission": new_sub,
        "ats_score": base_score
    }

# Trainer Protected Endpoints
@app.get("/api/trainer/submissions")
def get_trainer_submissions(user: Dict[str, Any] = Depends(require_permission("view_assigned_students"))):
    return {
        "batch": user.get("batch", "PPS4027 A"),
        "cohort_count": len(SUBMISSIONS_DB),
        "submissions": SUBMISSIONS_DB
    }

@app.post("/api/trainer/review")
def review_submission(
    payload: ReviewSubmissionRequest,
    user: Dict[str, Any] = Depends(require_permission("review_assigned_submission"))
):
    found = False
    for s in SUBMISSIONS_DB:
        if s["id"] == payload.submission_id:
            s["review_status"] = payload.review_status
            s["trainer_notes"] = payload.feedback_notes
            if payload.adjusted_score is not None:
                s["ats_score"] = payload.adjusted_score
            found = True
            break
            
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission '{payload.submission_id}' not found."
        )

    AUDIT_DB.insert(0, {
        "time": datetime.now().strftime("%d %b, %H:%M"),
        "event": f"Trainer evaluation published for {payload.submission_id}",
        "actor": f"{user['name']} ({user['id']})",
        "result": "Success",
        "category": "Grading"
    })

    return {"success": True, "message": "Review and grade recorded."}

# Admin Protected Endpoints
@app.get("/api/admin/audit-logs")
def get_admin_audit_logs(user: Dict[str, Any] = Depends(require_permission("view_audit_log"))):
    return {
        "count": len(AUDIT_DB),
        "logs": AUDIT_DB
    }

@app.get("/api/admin/system-config")
def get_system_config(user: Dict[str, Any] = Depends(require_permission("manage_configuration"))):
    return SYSTEM_CONFIG_DB

@app.post("/api/admin/system-config")
def update_system_config(
    payload: SystemConfigRequest,
    user: Dict[str, Any] = Depends(require_permission("manage_configuration"))
):
    SYSTEM_CONFIG_DB["retention_days"] = payload.retention_days
    SYSTEM_CONFIG_DB["ats_weights"] = payload.ats_weights
    SYSTEM_CONFIG_DB["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    AUDIT_DB.insert(0, {
        "time": datetime.now().strftime("%d %b, %H:%M"),
        "event": "System retention & ATS weight scheme updated",
        "actor": f"{user['name']} ({user['id']})",
        "result": "Success",
        "category": "Policy"
    })

    return {"success": True, "config": SYSTEM_CONFIG_DB}
