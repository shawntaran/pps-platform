import streamlit as st
from utils.mock_api import get_report
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("view_assigned_reports")
report = get_report(user, "sub_2026_014")

theme.page_header(
    "Resume Review — Evaluation Desk",
    "Aarav Mehta &nbsp;|&nbsp; CA1 Resume Review &nbsp;|&nbsp; Docket #14",
)

theme.stat_grid(
    theme.stat_card("ATS Overall",       f"{report['ats_score']} / 100"),
    theme.stat_card("Parseability",      f"{report['parseability']['score']} / 100"),
    theme.stat_card("Keyword Match",     f"{report['keyword_match']['score']} / 100"),
    theme.stat_card("Section Integrity", f"{report['section_structure']['score']} / 100"),
)

with st.container(border=True):
    theme.section_title("ATS & JD Breakdown")
    st.markdown(
        theme.score_bar("ATS Overall",         report["ats_score"])
        + theme.score_bar("Keyword Match",     report["keyword_match"]["score"])
        + theme.score_bar("Section Structure", report["section_structure"]["score"]),
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Detected sections**")
        for s in report["detected_sections"]:
            st.markdown(f"<span class='pps-tag'>{s}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown("**Matched skills**")
        for s in report["matched_skills"]:
            st.markdown(f"<span class='badge badge-complete'>{s}</span>", unsafe_allow_html=True)
    with c3:
        st.markdown("**Missing / gap skills**")
        for s in report["missing_skills"]:
            st.markdown(f"<span class='badge badge-waiting'>{s}</span>", unsafe_allow_html=True)

with st.form("trainer_review", border=True):
    theme.section_title("Evaluator Remark & Coaching Advisory")
    comments = st.text_area(
        "Trainer comments",
        placeholder="Add constructive, actionable feedback for the student.",
        height=130,
    )
    status = st.selectbox(
        "Review outcome",
        ["Needs review", "Conditional Pass", "Approved & Locked"],
    )
    save = st.form_submit_button(
        "Finalise & Publish Grade",
        type="primary",
        icon=":material/save:",
    )

if save:
    require_permission("review_assigned_submission")
    st.session_state.review_status = status
    st.success("Review saved in this prototype session.", icon=":material/check_circle:")
