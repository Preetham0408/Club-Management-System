# Owner: Person A. Shared look-and-feel: CSS and the sidebar user card.
import streamlit as st
from auth import logout
from constants import (
    SESSION_ROLE, SESSION_USER_ID, SESSION_USER_NAME,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN,
)

ROLE_LABELS = {
    SESSION_ROLE_STUDENT: "Student",
    SESSION_ROLE_HEAD: "Club Head",
    SESSION_ROLE_ADMIN: "Admin",
}

CSS = """
.block-container { padding-top: 2.5rem; }
[data-testid="stMetric"] {
    background: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 12px;
    padding: 14px 18px;
}
.hero { text-align: center; margin-bottom: 1rem; }
.hero h1 { font-size: 2.2rem; margin-bottom: 0.2rem; }
.hero p { opacity: 0.7; margin: 0; }
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def render_sidebar_user():
    """Who is logged in + Logout button, shown under the menu on every page."""
    with st.sidebar:
        st.divider()
        st.markdown(f"**{st.session_state[SESSION_USER_NAME]}**")
        st.caption(f"{ROLE_LABELS[st.session_state[SESSION_ROLE]]} · ID {st.session_state[SESSION_USER_ID]}")
        if st.button("🚪 Logout", key="sidebar_logout"):
            logout()
            st.rerun()