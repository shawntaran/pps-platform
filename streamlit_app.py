import streamlit as st

from utils.mock_api import USERS, authenticate
from utils import theme

st.set_page_config(
    page_title="PPS4027 Placement Portal",
    page_icon=":material/school:",
    layout="wide",
)

theme.inject_css()

# ── Session-state defaults ───────────────────────────────────────────────────
st.session_state.setdefault("current_user", None)
st.session_state.setdefault("consent_given", False)
st.session_state.setdefault("review_status", "Needs review")
st.session_state.setdefault("_auth_error", "")

# ── Sign-in screen ───────────────────────────────────────────────────────────
if st.session_state.current_user is None:
    st.markdown(
        """
        <div class="signin-wrap">
          <div class="signin-left">
            <div>
              <div class="signin-brand-chip">&#127979; PPS4027 Placement Portal</div>
              <div class="signin-headline">Prepare, practise,&nbsp;progress.</div>
              <div class="signin-sub">
                An integrated 15-week placement-preparation curriculum benchmarked
                against industry role standards, single-column ATS diagnostics,
                and rigorous faculty review.
              </div>
            </div>
            <div class="signin-footer">
              Verified institutional access for registered candidates,
              faculty mentors, and academic governance.
            </div>
          </div>
          <div class="signin-right">
            <div>
              <div style="font-size:1.4rem;font-weight:700;color:#191c1f;">Welcome back</div>
              <div style="font-size:.875rem;color:#42474c;margin-top:.25rem;">
                Sign in to continue your placement-training journey.
              </div>
            </div>
            <div class="signin-notice">
              <strong>Notice for Cohort Candidates:</strong>
              AY 2024&#8211;25 Continuous Assessment CA1 locking soon.
              Ensure you authenticate with your designated university address.
            </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Demo account selector (simulates "which credentials are you entering") ─
    account_key = st.selectbox(
        "Demo account (simulates credential lookup)",
        options=list(USERS),
        format_func=lambda k: f"{USERS[k]['name']} — {USERS[k]['email']}",
        key="signin_account",
        help="In production this would be your institutional email + password.",
    )

    # ── Claimed role selector (what role the user is asserting) ────────────────
    claimed_role = st.radio(
        "Claimed portal role",
        options=["student", "trainer", "admin"],
        format_func=lambda r: r.title(),
        horizontal=True,
        key="signin_role",
        help="Select the role you are accessing. Must match your registered account role.",
    )

    # Helper text showing expected destination
    _dest = {
        "student": "Student Dashboard",
        "trainer": "Trainer Dashboard & Evaluation Desk",
        "admin":   "Admin Governance Hub",
    }
    st.markdown(
        f"<div style='font-size:.78rem;color:#72787d;margin:.15rem 0 .6rem;'>"
        f"Claiming: <strong>{claimed_role.title()}</strong> &rarr; {_dest[claimed_role]}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Auth error banner (shown when validate fails) ──────────────────────────
    if st.session_state._auth_error:
        st.error(st.session_state._auth_error, icon=":material/lock:")

    # ── Sign-in button ─────────────────────────────────────────────────────────
    if st.button(
        "Sign in to Dashboard  \u2192",
        type="primary",
        use_container_width=True,
        key="signin_btn",
    ):
        # Backend RBAC validation — session state is ONLY written on success.
        try:
            verified_user = authenticate(account_key, claimed_role)
            st.session_state.current_user = verified_user
            st.session_state._auth_error = ""
            st.rerun()
        except PermissionError as exc:
            # Role mismatch — keep current_user as None, show error.
            st.session_state._auth_error = str(exc)
            st.rerun()
        except KeyError as exc:
            st.session_state._auth_error = str(exc)
            st.rerun()

    st.markdown(
        """
            <div style="display:flex;gap:.75rem;flex-wrap:wrap;margin-top:.5rem;">
              <span class="pps-tag">Student: Portfolio &amp; ATS</span>
              <span class="pps-tag">Trainer: Rubrics &amp; Mock Vivas</span>
              <span class="pps-tag">Admin: Cohort Analytics</span>
            </div>
            <div style="font-size:.75rem;color:#72787d;margin-top:.5rem;">
              Your dashboard and permissions are determined by your verified account role.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ── Sidebar (post sign-in) ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:.5rem;padding:.25rem 0 .75rem;">
          <span style="font-size:1.4rem;">&#127979;</span>
          <div>
            <div style="font-weight:700;font-size:.95rem;color:#191c1f;">PPS4027</div>
            <div style="font-size:.72rem;color:#72787d;">Placement Portal</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user = st.session_state.current_user
    role = user["role"]

    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #c2c7cd;border-radius:8px;
                    padding:.6rem .85rem;margin-bottom:.75rem;">
          <div style="font-size:.82rem;font-weight:600;color:#191c1f;">{user["name"]}</div>
          <div style="font-size:.72rem;color:#72787d;">{user["email"]}</div>
          <div style="margin-top:.3rem;">
            <span class="badge badge-active">{role.title()}</span>
            <span style="font-size:.72rem;color:#72787d;margin-left:.4rem;">{user["batch"]}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Sign out",
        icon=":material/logout:",
        use_container_width=True,
        key="signout_btn",
    ):
        st.session_state.current_user = None
        st.session_state.consent_given = False
        st.rerun()

# ── Page groups ──────────────────────────────────────────────────────────────
student_pages = [
    st.Page("app_pages/student_dashboard.py",  title="Dashboard",        icon=":material/dashboard:"),
    st.Page("app_pages/resume_review.py",      title="Resume review",    icon=":material/description:"),
    st.Page("app_pages/student_history.py",    title="Analysis history", icon=":material/history:"),
    st.Page("app_pages/student_privacy.py",    title="Privacy & data",   icon=":material/shield:"),
]

trainer_pages = [
    st.Page("app_pages/trainer_dashboard.py",  title="Trainer dashboard", icon=":material/monitoring:"),
    st.Page("app_pages/trainer_reviews.py",    title="Resume reviews",    icon=":material/rate_review:"),
]

admin_pages = [
    st.Page("app_pages/admin_console.py",      title="Administration",    icon=":material/admin_panel_settings:"),
]

pages = (
    {"Student": student_pages} if role == "student"
    else {"Trainer": trainer_pages} if role == "trainer"
    else {"Admin": admin_pages}
)

st.navigation(pages, position="sidebar").run()
