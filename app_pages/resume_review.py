import streamlit as st
from utils.mock_api import get_report, submit_resume
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("submit_resume")

theme.page_header(
    "Resume Review &amp; Diagnostic Desk",
    "Submit your resume for automated formatting, section parseability, "
    "and keyword calibration against target industry job descriptions.",
)

consent_done = st.session_state.get("consent_given", False)
steps = [
    ("Upload Resume",    "done"   if consent_done else "active"),
    ("Target Role & JD","done"   if consent_done else "pending"),
    ("Privacy & Consent","done"  if consent_done else "pending"),
    ("Automated Analysis","done" if consent_done else "pending"),
    ("Diagnostic Report","done"  if consent_done else "pending"),
]
theme.step_strip(steps)

with st.form("resume_submission", border=True):
    theme.section_title("Configured Artifacts")
    resume = st.file_uploader(
        "Resume file (PDF or DOCX, up to 5 MB)",
        type=["pdf", "docx"],
        max_upload_size=5,
        help="Single-column ATS-safe layout recommended.",
    )
    target_jd = st.text_area(
        "Target job description (optional)",
        placeholder="Paste the full job description here to calibrate keyword match.",
        height=120,
    )
    st.markdown(
        """<div class='pps-consent'>
          <div class='pps-consent-title'>&#128737; Academic Data Processing &amp; Consent Notice</div>
          <div class='pps-consent-body'>
            <strong>What is analysed:</strong> Text layers of your submitted PDF,
            extracted heading structures, and matched job-description text.<br><br>
            <strong>Academic formative purpose:</strong> Processing produces rubric scores
            and corrective syntactic feedback strictly for PPS4027 faculty mentoring.
            Your resume is never circulated to recruitment agencies without your sign-off.<br><br>
            <strong>Ephemeral 30-day retention:</strong> All parsed candidate cache is
            automatically purged 30 calendar days following semester grade ratification.
          </div>
        </div>""",
        unsafe_allow_html=True,
    )
    consent = st.checkbox(
        "I consent to processing my resume and JD for PPS4027 placement-training feedback."
    )
    submitted = st.form_submit_button(
        "Run Diagnostic Analysis  \u2192",
        type="primary",
        icon=":material/analytics:",
    )

if submitted:
    if not resume:
        st.error("Upload a PDF or DOCX resume to continue.")
    elif not consent:
        st.error("Consent is required before analysis can begin.")
    else:
        st.session_state.consent_given = True
        result = submit_resume(user, resume.name, target_jd)
        st.success(
            f"{result['filename']} queued for analysis.",
            icon=":material/check_circle:",
        )

if st.session_state.get("consent_given"):
    report = get_report(user, "sub_2026_014")
    st.divider()
    theme.page_header(
        "Latest Diagnostic Report",
        f"Status: {report['status']} &nbsp;|&nbsp; {report['analysed_on']}",
    )
    with st.container(border=True):
        theme.section_title("Explainable Metrics — Weighted Scores")
        st.markdown(
            theme.score_bar("ATS Compatibility",     report["ats_score"])
            + theme.score_bar("Parseability",        report["parseability"]["score"])
            + theme.score_bar("Keyword JD Alignment",report["keyword_match"]["score"])
            + theme.score_bar("Structural Integrity",report["section_structure"]["score"]),
            unsafe_allow_html=True,
        )

    score_tab, skills_tab, recs_tab = st.tabs(
        ["Score breakdown", "Skills & sections", "Recommendations"]
    )
    with score_tab:
        for label, detail in [
            ("Parseability",      report["parseability"]),
            ("Keyword match",     report["keyword_match"]),
            ("Section structure", report["section_structure"]),
        ]:
            st.markdown(f"**{label} — {detail['score']}/100**")
            st.caption(detail["summary"])
            st.markdown("---")
    with skills_tab:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Detected sections**")
            for s in report["detected_sections"]: st.markdown(f"- {s}")
        with c2:
            st.markdown("**Matched skills**")
            for s in report["matched_skills"]: st.markdown(f"- ✅ {s}")
        with c3:
            st.markdown("**Skills to strengthen**")
            for s in report["missing_skills"]: st.markdown(f"- ⚠️ {s}")
    with recs_tab:
        st.markdown("**Formatting issues**")
        for item in report["formatting_issues"]:
            st.warning(item, icon=":material/warning:")
        st.markdown("**Recommended next steps**")
        for item in report["recommendations"]:
            st.markdown(f"- {item}")
