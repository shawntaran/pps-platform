import streamlit as st

ROLE_PERMISSIONS = {
    "student": {
        "view_own_profile",
        "submit_resume",
        "view_own_report",
        "manage_own_privacy",
    },
    "trainer": {
        "view_assigned_students",
        "view_assigned_reports",
        "review_assigned_submission",
    },
    "admin": {
        "manage_users",
        "manage_configuration",
        "view_audit_log",
    },
}


def current_user():
    user = st.session_state.get("current_user")

    if not user:
        st.error("Select a demo account to continue.")
        st.stop()

    return user


def require_permission(permission):
    """Backend-style permission guard for protected actions."""

    user = current_user()

    if permission not in ROLE_PERMISSIONS.get(user["role"], set()):
        st.error("You do not have permission to access this information.")
        st.stop()

    return user