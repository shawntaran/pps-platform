import streamlit as st
from utils.mock_api import trainer_submissions
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("view_assigned_students")
rows = trainer_submissions(user)

theme.page_header(
    "Trainer Dashboard — Evaluation Desk",
    f"Batch {user['batch']} &nbsp;|&nbsp; CA1 Submission &amp; Evaluation Desk",
)

complete    = sum(r["status"] == "Complete" for r in rows)
pending_rev = sum(r["review"] == "Needs review" for r in rows)
ats_scores  = [r["ats_score"] for r in rows if r["ats_score"]]
avg_ats     = int(sum(ats_scores) / len(ats_scores)) if ats_scores else 0

theme.stat_grid(
    theme.stat_card("Cohort enrolled",   str(len(rows)), "Section Track"),
    theme.stat_card("Analyses complete", f"{complete} / {len(rows)}",
                    f"{int(complete/len(rows)*100)}% complete"),
    theme.stat_card("Pending review",    str(pending_rev), "Needs evaluator action"),
    theme.stat_card("Batch ATS avg.",    f"{avg_ats} / 100"),
)

with st.container(border=True):
    theme.section_title("Submissions Ledger — CA1 Resume Building & ATS")
    header = (
        "<div class='pps-row' style='font-size:.72rem;font-weight:600;color:#72787d;padding-bottom:.4rem;'>"
        "<div style='width:32px'></div>"
        "<div class='pps-row-main'>Student</div>"
        "<div style='width:90px;text-align:center;'>Assessment</div>"
        "<div style='width:110px;text-align:center;'>ATS Match</div>"
        "<div style='width:120px;text-align:right;'>Status / Review</div>"
        "</div>"
    )
    rows_html = header
    for r in rows:
        ats = r["ats_score"]
        if ats:
            bar_html = (
                f"<div style='width:110px;'>"
                f"<div style='height:6px;background:#e7e8ec;border-radius:99px;overflow:hidden;'>"
                f"<div style='height:100%;width:{ats}%;background:#4a6b82;border-radius:99px;'></div>"
                f"</div>"
                f"<div style='font-size:.72rem;font-weight:700;color:#191c1f;text-align:center;margin-top:2px;'>{ats}/100</div>"
                f"</div>"
            )
        else:
            bar_html = "<div style='width:110px;text-align:center;font-size:.75rem;color:#72787d;'>—</div>"

        sk = "complete" if r["status"] == "Complete" else "active" if r["status"] == "Processing" else "pending"
        rk = "error" if r["review"] == "Needs review" else "pending"

        rows_html += (
            f"<div class='pps-row'>"
            f"<div class='pps-row-icon' style='background:#315369;color:#fff;font-weight:700;font-size:.75rem;'>"
            f"{r['student'][0]}</div>"
            f"<div class='pps-row-main'>"
            f"<div class='pps-row-title'>{r['student']}</div>"
            f"<div class='pps-row-sub'>CA1 Resume Review</div></div>"
            f"<div style='width:90px;text-align:center;'>"
            f"<span class='badge badge-active'>{r['assessment']}</span></div>"
            f"{bar_html}"
            f"<div style='width:120px;text-align:right;'>"
            f"<span class='badge badge-{sk}'>{r['status']}</span><br>"
            f"<span class='badge badge-{rk}' style='margin-top:.2rem;'>{r['review']}</span>"
            f"</div></div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)
