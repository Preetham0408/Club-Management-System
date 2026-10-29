import streamlit as st
from database import fetch_one
from constants import (
    SESSION_LOGGED_IN, SESSION_ROLE, SESSION_USER_ID, SESSION_USER_NAME, SESSION_CLUB_ID,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN, ROLE_HEAD,
)

DEFAULTS = {
    SESSION_LOGGED_IN: False,
    SESSION_ROLE: None,
    SESSION_USER_ID: None,
    SESSION_USER_NAME: None,
    SESSION_CLUB_ID: None,
}

def init_session():
    """Create every session key once, if it doesn't exist yet."""
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

def require_role(allowed_roles):
    """Stop the page unless a logged-in user has one of the allowed roles."""
    init_session()
    if not st.session_state[SESSION_LOGGED_IN]:
        st.error("Please log in on the main page first.")
        st.stop()
    if st.session_state[SESSION_ROLE] not in allowed_roles:
        st.error("Your role cannot open this page.")
        st.stop()

def _start_session(role, user_id, name, club_id=None):
    st.session_state[SESSION_LOGGED_IN] = True
    st.session_state[SESSION_ROLE] = role
    st.session_state[SESSION_USER_ID] = user_id
    st.session_state[SESSION_USER_NAME] = name
    st.session_state[SESSION_CLUB_ID] = club_id

def login_student(student_id):
    row = fetch_one("SELECT student_id, name FROM Student WHERE student_id = %s", (student_id,))
    if row is None:
        return False
    _start_session(SESSION_ROLE_STUDENT, row["student_id"], row["name"])
    return True

def login_head(student_id):
    row = fetch_one(
        "SELECT s.student_id, s.name, cm.club_id "
        "FROM Student s JOIN Club_Memberships cm ON s.student_id = cm.student_id "
        "WHERE s.student_id = %s AND cm.role = %s",
        (student_id, ROLE_HEAD),
    )
    if row is None:
        return False
    _start_session(SESSION_ROLE_HEAD, row["student_id"], row["name"], row["club_id"])
    return True

def login_admin(admin_id):
    """admin_id must already be an int (main.py checks this)."""
    row = fetch_one("SELECT admin_id, name FROM Admin WHERE admin_id = %s", (admin_id,))
    if row is None:
        return False
    _start_session(SESSION_ROLE_ADMIN, row["admin_id"], row["name"])
    return True

def logout():
    for key in DEFAULTS:
        st.session_state.pop(key, None)