import streamlit as st
from utils.mock_api import get_report
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("view_own_report")
report = get_report(user, "sub_2026_014")

theme.page_header(
    "Analysis History",
    "Compare your resume iterations against varying job roles.",
)

history = [
    {
        "Date":      report["analysed_on"],
        "File":      "Aarav_Mehta_Resume.pdf",
        "ATS score": report["ats_score"],
        "Status":    report["status"],
        "Target JD": "Data analyst",
    }
]

with st.container(border=True):
    theme.section_title("Recent Resumes & Historical Audits")
    header = (
        "<div class='pps-row' style='font-size:.72rem;font-weight:600;color:#72787d;padding-bottom:.4rem;'>"
        "<div style='width:32px'></div>"
        "<div class='pps-row-main'>Resume file &nbsp;|&nbsp; Target JD</div>"
        "<div style='width:80px;text-align:center;'>ATS Score</div>"
        "<div style='width:80px;text-align:center;'>Date</div>"
        "<div style='width:80px;text-align:right;'>Status</div>"
        "</div>"
    )
    rows_html = header
    for h in history:
        sc = "#065f46" if h["ATS score"] >= 70 else "#92400e"
        rows_html += (
            f"<div class='pps-row'>"
            f"<div class='pps-row-icon'>&#128196;</div>"
            f"<div class='pps-row-main'>"
            f"<div class='pps-row-title'>{h['File']}</div>"
            f"<div class='pps-row-sub'>{h['Target JD']}</div>"
            f"</div>"
            f"<div style='width:80px;text-align:center;font-weight:700;color:{sc};'>{h['ATS score']}/100</div>"
            f"<div style='width:80px;text-align:center;font-size:.78rem;color:#42474c;'>{h['Date']}</div>"
            f"<div style='width:80px;text-align:right;'>"
            f"<span class='badge badge-complete'>{h['Status']}</span></div>"
            f"</div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)

st.caption("The final version will load this history from the protected submissions API.")
