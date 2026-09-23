import streamlit as st
from utils.mock_api import assignments, calendar_events, content_library, student_overview
from utils.security import require_permission
from utils import theme

theme.inject_css()
user = require_permission("view_own_profile")
overview = student_overview(user["id"])

theme.greeting(
    user["name"],
    f"{overview['active_module']} &nbsp;|&nbsp; Batch {user['batch']}",
)

theme.stat_grid(
    theme.stat_card("Course completion", f"{overview['completion']}%", "Week 4 of 15"),
    theme.stat_card("Next deadline",     overview["next_deadline"]),
    theme.stat_card("Current assessment","CA1", "Resume review"),
)

left, right = st.columns((3, 2), gap="medium")

with left:
    with st.container(border=True):
        theme.section_title("Content Library")
        lib = content_library()
        rows_html = ""
        for item in lib:
            rel_badge = (
                "<span class='badge badge-complete'>Released</span>"
                if item["released"]
                else "<span class='badge badge-notopen'>Coming soon</span>"
            )
            rows_html += (
                f"<div class='pps-row'>"
                f"<div class='pps-row-icon'>&#128218;</div>"
                f"<div class='pps-row-main'>"
                f"<div class='pps-row-title'>{item['title']}</div>"
                f"<div class='pps-row-sub'>{item['week']} &middot; {item['type']}</div>"
                f"</div>{rel_badge}</div>"
            )
        st.markdown(rows_html, unsafe_allow_html=True)

    with st.container(border=True):
        theme.section_title("Your Assignments")
        assign = assignments(user["id"])
        rows_html = ""
        for a in assign:
            sk = (
                "complete" if a["status"] == "Complete"
                else "notopen" if a["status"] == "Not open"
                else "active"
            )
            rows_html += (
                f"<div class='pps-row'>"
                f"<div class='pps-row-icon'>&#128203;</div>"
                f"<div class='pps-row-main'>"
                f"<div class='pps-row-title'>{a['assessment']} &mdash; {a['title']}</div>"
                f"<div class='pps-row-sub'>Due {a['due']} &nbsp;&middot;&nbsp; Score: {a['score']}</div>"
                f"</div><span class='badge badge-{sk}'>{a['status']}</span></div>"
            )
        st.markdown(rows_html, unsafe_allow_html=True)

with right:
    with st.container(border=True):
        theme.section_title("Upcoming Calendar")
        cal = calendar_events()
        rows_html = ""
        for ev in cal:
            rows_html += (
                f"<div class='pps-row'>"
                f"<div class='pps-row-icon'>&#128197;</div>"
                f"<div class='pps-row-main'>"
                f"<div class='pps-row-title'>{ev['event']}</div>"
                f"<div class='pps-row-sub'>{ev['date']} &middot; {ev['location']}</div>"
                f"</div></div>"
            )
        st.markdown(rows_html, unsafe_allow_html=True)

    with st.container(border=True):
        theme.section_title("Reminders")
        for r in overview["reminders"]:
            st.markdown(
                f"<div class='pps-row'>"
                f"<div class='pps-row-icon'>&#128276;</div>"
                f"<div class='pps-row-main'>"
                f"<div class='pps-row-title'>{r}</div>"
                f"</div><span class='badge badge-new'>New</span></div>",
                unsafe_allow_html=True,
            )
