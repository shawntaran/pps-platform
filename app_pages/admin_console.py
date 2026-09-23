import streamlit as st
from utils.mock_api import USERS, audit_events, system_configuration
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("manage_users")

theme.page_header(
    "System Administration &amp; Governance",
    "Operational controls for course cohort permissions, continuous assessment "
    "deadlines, evaluation weighting schemes, and immutable audit logs.",
)

config = system_configuration()

theme.stat_grid(
    theme.stat_card("Active Users",          "1,248", "1,180 Students · 42 Faculty · 6 Admins"),
    theme.stat_card("Continuous Assessment", "CA1 Active", "30% weightage"),
    theme.stat_card("Compliance & Consent",  "99.4%", "1,173 / 1,180 signed"),
    theme.stat_card("ATS Engine",            "Healthy", "v4.2 · Zero queue backlog"),
)

users_tab, config_tab, audit_tab = st.tabs([
    "&#128100; Users & Roles",
    "&#9881;&#65039; System Configuration",
    "&#128274; Audit & Compliance",
])

with users_tab:
    require_permission("manage_users")
    theme.section_title("Directory & Role Delegation")
    user_list = [{"name": v["name"], "email": v["email"],
                  "role": v["role"], "batch": v["batch"]} for v in USERS.values()]
    role_kind = {"student": "active", "trainer": "new", "admin": "error"}
    header = (
        "<div class='pps-row' style='font-size:.72rem;font-weight:600;color:#72787d;padding-bottom:.35rem;'>"
        "<div style='width:32px'></div><div class='pps-row-main'>Name / Email</div>"
        "<div style='width:80px;text-align:center;'>Role</div>"
        "<div style='width:110px;text-align:right;'>Batch</div></div>"
    )
    rows_html = header
    for u in user_list:
        initials = "".join(part[0] for part in u["name"].split()[:2])
        rows_html += (
            f"<div class='pps-row'>"
            f"<div class='pps-row-icon' style='background:#315369;color:#fff;font-weight:700;font-size:.72rem;'>{initials}</div>"
            f"<div class='pps-row-main'>"
            f"<div class='pps-row-title'>{u['name']}</div>"
            f"<div class='pps-row-sub'>{u['email']}</div></div>"
            f"<div style='width:80px;text-align:center;'>"
            f"<span class='badge badge-{role_kind.get(u['role'],'pending')}'>{u['role'].title()}</span></div>"
            f"<div style='width:110px;text-align:right;font-size:.78rem;color:#42474c;'>{u['batch']}</div>"
            f"</div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)
    st.caption("Role changes will call the identity service in the production version.")

with config_tab:
    require_permission("manage_configuration")
    theme.section_title("System Configuration")
    theme.stat_grid(
        theme.stat_card("Max Upload Size",   f"{config['max_upload_mb']} MB"),
        theme.stat_card("Default Retention", f"{config['retention_days']} days"),
    )
    with st.container(border=True):
        theme.section_title("Continuous Assessment Schedule")
        ca_items = [
            ("CA1", "Resume Engineering & ATS Parsing",     "Active Deadline",    "badge-error",
             "Oct 01, 2024 · Weightage: 30%", "Hard lock: Oct 28, 2024 · 23:59 IST"),
            ("CA2", "Group Discussion & Rhetoric Rubric",    "Pending Launch",     "badge-pending",
             "Nov 04 – Nov 25, 2024 · Weightage: 35%", "Hard lock: Nov 25, 2024 · 23:59 IST"),
            ("CA3", "Personal Interview Simulation Clinic",  "Draft Specification","badge-notopen",
             "Dec 02 – Dec 20, 2024 · Weightage: 35%", "Hard lock: Dec 20, 2024 · 18:00 IST"),
        ]
        ca_html = ""
        for code, title, stxt, scls, dates, deadline in ca_items:
            ca_html += (
                f"<div class='pps-row'>"
                f"<div class='pps-row-icon' style='background:#315369;color:#fff;font-weight:700;font-size:.72rem;'>{code}</div>"
                f"<div class='pps-row-main'>"
                f"<div class='pps-row-title'>{title}</div>"
                f"<div class='pps-row-sub'>{dates} &nbsp;|&nbsp; {deadline}</div></div>"
                f"<span class='badge {scls}'>{stxt}</span></div>"
            )
        st.markdown(ca_html, unsafe_allow_html=True)
    st.markdown("**ATS Score Weights**")
    for comp, wt in config["ats_weights"].items():
        st.markdown(
            f"<span class='pps-tag'>{comp}</span> "
            f"<span class='badge badge-active'>{wt}%</span>",
            unsafe_allow_html=True,
        )

with audit_tab:
    require_permission("view_audit_log")
    theme.section_title("Forensic Trail — Live Audit Log")
    events = audit_events(user)
    rows_html = ""
    for ev in events:
        rk = "complete" if ev["result"] in ("Allowed", "Success") else "error"
        rows_html += (
            f"<div class='pps-row'>"
            f"<div class='pps-row-icon'>&#128274;</div>"
            f"<div class='pps-row-main'>"
            f"<div class='pps-row-title'>{ev['event']}</div>"
            f"<div class='pps-row-sub'>{ev['time']} &nbsp;·&nbsp; Actor: {ev['actor']}</div></div>"
            f"<span class='badge badge-{rk}'>{ev['result']}</span></div>"
        )
    st.markdown(rows_html, unsafe_allow_html=True)
    st.caption("Audit records are intentionally restricted to admins.")
