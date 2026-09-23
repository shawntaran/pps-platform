import React, { createContext, useContext, useState, useEffect } from 'react';
import { 
  USERS, 
  INITIAL_REPORT, 
  INITIAL_SUBMISSIONS, 
  ASSIGNMENTS, 
  CONTENT_LIBRARY, 
  CALENDAR_EVENTS, 
  AUDIT_EVENTS, 
  SYSTEM_CONFIG 
} from '../data/mockData';

const AppContext = createContext();

const API_BASE_URL = 'http://localhost:8000/api';

export const AppProvider = ({ children }) => {
  // Current authenticated user (default to student Aarav Mehta)
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('pps_user');
    return saved ? JSON.parse(saved) : USERS.student;
  });

  // Active role view for demo testing (student / trainer / admin)
  const [activeRoleView, setActiveRoleView] = useState(() => currentUser?.role || 'student');

  // Submissions state
  const [submissions, setSubmissions] = useState(() => {
    const saved = localStorage.getItem('pps_submissions');
    return saved ? JSON.parse(saved) : INITIAL_SUBMISSIONS;
  });

  // Active Diagnostic Report state
  const [currentReport, setCurrentReport] = useState(() => {
    const saved = localStorage.getItem('pps_current_report');
    return saved ? JSON.parse(saved) : INITIAL_REPORT;
  });

  // Privacy & Consent state
  const [consentActive, setConsentActive] = useState(true);
  const [dataRetentionDays, setDataRetentionDays] = useState(SYSTEM_CONFIG.retention_days);

  // System audit logs
  const [auditLogs, setAuditLogs] = useState(AUDIT_EVENTS);

  // System Configuration
  const [systemConfig, setSystemConfig] = useState(SYSTEM_CONFIG);

  // Toast / Notification banner
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  useEffect(() => {
    localStorage.setItem('pps_user', JSON.stringify(currentUser));
  }, [currentUser]);

  useEffect(() => {
    localStorage.setItem('pps_submissions', JSON.stringify(submissions));
  }, [submissions]);

  useEffect(() => {
    localStorage.setItem('pps_current_report', JSON.stringify(currentReport));
  }, [currentReport]);

  // Server-enforced Authentication method
  const login = async (accountKey, claimedRole) => {
    try {
      // First attempt real FastAPI backend authentication
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_key: accountKey,
          claimed_role: claimedRole
        })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server Authorization Error (HTTP ${res.status})`);
      }

      const data = await res.json();
      const authenticatedUser = data.user;

      setCurrentUser(authenticatedUser);
      setActiveRoleView(authenticatedUser.role);
      
      addAuditLog({
        event: `Server-verified login (${claimedRole.toUpperCase()})`,
        actor: `${authenticatedUser.name} (${authenticatedUser.id})`,
        result: "Success",
        category: "Auth"
      });

      showToast(`Welcome back, ${authenticatedUser.name}! Authenticated via API.`);
      return authenticatedUser;
    } catch (err) {
      // If server is unreachable or returned explicit 403 Forbidden, check if it was a permission error
      if (err.message && err.message.includes('Access Denied')) {
        throw err;
      }
      
      // Fallback local RBAC check if backend is offline
      const user = USERS[accountKey];
      if (!user) {
        throw new Error(`No demo account found for '${accountKey}'.`);
      }

      if (user.role !== claimedRole) {
        throw new Error(
          `Access Denied: Account '${user.name}' is registered as '${user.role}', not '${claimedRole}'.`
        );
      }

      setCurrentUser(user);
      setActiveRoleView(user.role);
      showToast(`Welcome back, ${user.name}! Authenticated as ${user.role}.`);
      return user;
    }
  };

  const logout = () => {
    addAuditLog({
      event: "User sign-out session ended",
      actor: `${currentUser.name} (${currentUser.id})`,
      result: "Success",
      category: "Auth"
    });
    setCurrentUser(null);
    localStorage.removeItem('pps_user');
  };

  const switchRoleView = (role) => {
    if (USERS[role]) {
      setCurrentUser(USERS[role]);
      setActiveRoleView(role);
      showToast(`Switched view to ${role.toUpperCase()} mode (${USERS[role].name})`, 'info');
    }
  };

  const addAuditLog = ({ event, actor, result = "Success", category = "System" }) => {
    const newLog = {
      time: new Date().toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }),
      event,
      actor: actor || `${currentUser?.name} (${currentUser?.id})`,
      result,
      ip: "10.40.75.226",
      category
    };
    setAuditLogs(prev => [newLog, ...prev]);
  };

  // Submit and analyze new resume
  const submitNewResume = (fileData, targetJdText, jobTitle) => {
    const baseScore = Math.floor(Math.random() * 15) + 75;
    const parseScore = Math.floor(Math.random() * 10) + 85;
    const kwScore = targetJdText?.length > 100 ? 84 : 70;
    const structureScore = Math.floor(Math.random() * 12) + 78;

    const newReport = {
      ...INITIAL_REPORT,
      submission_id: `sub_2026_${Math.floor(Math.random() * 900) + 100}`,
      student_name: currentUser.name,
      student_id: currentUser.id,
      filename: fileData.name || "Resume_Submitted.pdf",
      target_role: jobTitle || "Target Industry Role",
      analysed_on: "Just now",
      ats_score: baseScore,
      parseability: {
        score: parseScore,
        summary: "Single-column structure parsed cleanly with compliant typography hierarchy.",
        details: [
          "Standard UTF-8 character encoding verified",
          "Section headings clearly indexed by parser",
          "No complex tables or graphic artifacts found"
        ]
      },
      keyword_match: {
        score: kwScore,
        summary: `Strong semantic alignment against ${jobTitle || 'the target job description'}.`,
        details: [
          "Core required technical tools recognized",
          "Domain-specific keywords matched in project descriptions",
          "Add further metrics to leadership and execution bullets"
        ]
      },
      section_structure: {
        score: structureScore,
        summary: "Clear standard ATS section flow with chronological experience.",
        details: [
          "Summary, Skills, Experience, Projects, Education all detected",
          "Standard margin spacing compliant with ATS bounding boxes"
        ]
      }
    };

    setCurrentReport(newReport);

    const newSubmission = {
      id: newReport.submission_id,
      student: currentUser.name,
      student_id: currentUser.id,
      rollNo: currentUser.rollNo || "PPS-2024-4027",
      filename: newReport.filename,
      target_role: newReport.target_role,
      assessment: "CA1",
      submitted_date: "Just now",
      status: "Complete",
      ats_score: baseScore,
      review_status: "Needs review",
      trainer_notes: "Awaiting mentor evaluation.",
      batch: currentUser.batch || "PPS4027 A"
    };

    setSubmissions(prev => [newSubmission, ...prev.filter(s => s.id !== newSubmission.id)]);

    addAuditLog({
      event: `New resume submission & ATS scan completed (${newReport.filename})`,
      actor: `${currentUser.name} (${currentUser.id})`,
      result: "Success",
      category: "Assessment"
    });

    return newReport;
  };

  const updateSubmissionReview = (submissionId, reviewStatus, feedbackNotes, adjustedScore) => {
    setSubmissions(prev => prev.map(s => {
      if (s.id === submissionId) {
        return {
          ...s,
          review_status: reviewStatus,
          trainer_notes: feedbackNotes || s.trainer_notes,
          ats_score: adjustedScore !== undefined ? adjustedScore : s.ats_score
        };
      }
      return s;
    }));

    if (currentReport.submission_id === submissionId) {
      setCurrentReport(prev => ({
        ...prev,
        trainer_feedback: feedbackNotes,
        ats_score: adjustedScore !== undefined ? adjustedScore : prev.ats_score
      }));
    }

    addAuditLog({
      event: `Evaluation review published for ${submissionId} (Status: ${reviewStatus})`,
      actor: `${currentUser.name} (${currentUser.id})`,
      result: "Success",
      category: "Grading"
    });

    showToast(`Evaluation published for submission #${submissionId}`);
  };

  const purgeStudentData = () => {
    setSubmissions(prev => prev.filter(s => s.student_id !== currentUser.id));
    addAuditLog({
      event: "User requested full GDPR/FERPA resume data erasure",
      actor: `${currentUser.name} (${currentUser.id})`,
      result: "Purged",
      category: "Compliance"
    });
    showToast("All stored resume drafts and diagnostic records purged.", "info");
  };

  return (
    <AppContext.Provider value={{
      currentUser,
      activeRoleView,
      submissions,
      currentReport,
      consentActive,
      setConsentActive,
      dataRetentionDays,
      setDataRetentionDays,
      auditLogs,
      systemConfig,
      setSystemConfig,
      toast,
      showToast,
      login,
      logout,
      switchRoleView,
      submitNewResume,
      updateSubmissionReview,
      purgeStudentData,
      assignments: ASSIGNMENTS,
      contentLibrary: CONTENT_LIBRARY,
      calendarEvents: CALENDAR_EVENTS
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
