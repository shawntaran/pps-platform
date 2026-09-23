import streamlit as st
from utils.security import require_permission
from utils import theme

theme.inject_css()
require_permission("manage_own_privacy")

theme.page_header(
    "Privacy &amp; Personal Data",
    "Clear, transparent information about how your resume drafts, skill assessments, "
    "and career coaching records are handled within the PPS4027 curriculum.",
)

if st.session_state.get("consent_given"):
    st.success(
        "Resume-Processing Consent Active — Signed for Cohort AY 2024-25",
        icon=":material/verified:",
    )
else:
    st.warning(
        "Consent will be requested when you submit a resume for analysis.",
        icon=":material/pending:",
    )

with st.container(border=True):
    theme.section_title("What Data We Process — 4 Categories")
    items = [
        ("&#128203;", "Resume Content &amp; History", "Continuous Assessment",
         "Text of your education, projects, technical skills, and internship history. "
         "Processed solely to generate structural formatting guidance, keyword alignment, "
         "and rubric scoring for CA1."),
        ("&#128247;", "Contact &amp; Header Information", "Never Shared Outward",
         "Institutional email address, contact telephone, and LinkedIn profile URLs. "
         "Parsed strictly to verify professional header completeness."),
        ("&#128188;", "Target Job Descriptions", "Benchmarking",
         "The job roles, responsibilities, and qualification texts you paste into Module 1 "
         "workshops. Used locally to evaluate how effectively your profile aligns with "
         "realistic market demands."),
        ("&#128200;", "Analysis &amp; Diagnostic Feedback", "Formative Only",
         "Quantitative and qualitative scores saved to your personal dashboard so you "
         "can address gaps ahead of formal campus recruitment drives."),
    ]
    rows_html = ""
    for icon, title, tag, desc in items:
        rows_html += (
            f"<div class='pps-info-item'>"
            f"<div class='pps-info-icon'>{icon}</div>"
            f"<div style='flex:1;'>"
            f"<div style='display:flex;align-items:center;gap:.5rem;'>"
            f"<div class='pps-info-title'>{title}</div>"
            f"<span class='badge badge-active'>{tag}</span></div>"
            f"<div class='pps-info-desc'>{desc}</div>"
            f"</div></div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="medium")
with c1:
    with st.container(border=True):
        theme.section_title("Your Data Controls")
        st.markdown(
            "<div style='font-size:.82rem;color:#42474c;margin-bottom:.75rem;'>"
            "You maintain full autonomy over your records.</div>",
            unsafe_allow_html=True,
        )
        st.button("Download Data Archive (.zip)", icon=":material/download:",
                  use_container_width=True)
        st.caption(
            "Exports all submitted resume drafts, targeted job roles, "
            "and diagnostic reports in a single folder."
        )

with c2:
    with st.container(border=True):
        theme.section_title("Course Processing Consent")
        st.markdown(
            "<div style='font-size:.82rem;color:#42474c;margin-bottom:.75rem;'>"
            "You can withdraw processing permission at any time.</div>",
            unsafe_allow_html=True,
        )
        st.button("Request deletion after grading", icon=":material/delete:",
                  use_container_width=True)
        st.caption(
            "Prototype controls — the privacy service will later provide "
            "the real retention and deletion workflow."
        )

st.markdown(
    """<div class='pps-card-low' style='margin-top:.5rem;'>
      <div style='font-style:italic;color:#42474c;font-size:.875rem;line-height:1.6;'>
        &#8220;Our curriculum exists to empower your career trajectory, not to score or
        index you for third parties. You hold ownership of your credentials and your
        career story.&#8221;
      </div>
      <div style='font-size:.75rem;color:#72787d;margin-top:.5rem;'>
        &#8212; Academic Directorate, Vocational Training
      </div>
    </div>""",
    unsafe_allow_html=True,
)
