import streamlit as st
from database import fetch_one
from constants import SESSION_LOGGED_IN, SESSION_ROLE, SESSION_USER_ID, SESSION_USER_NAME, SESSION_CLUB_ID, ROLE_HEAD

def init_session():
    """Initialize all session state keys on app load."""
    if SESSION_LOGGED_IN not in st.session_state:
        st.session_state[SESSION_LOGGED_IN] = False
    if SESSION_ROLE not in st.session_state:
        st.session_state[SESSION_ROLE] = None
    if SESSION_USER_ID not in st.session_state:
        st.session_state[SESSION_USER_ID] = None
    if SESSION_USER_NAME not in st.session_state:
        st.session_state[SESSION_USER_NAME] = None
    if SESSION_CLUB_ID not in st.session_state:
        st.session_state[SESSION_CLUB_ID] = None

def require_role(allowed_roles):
    """
    Guard: stop if user is not logged in or not in allowed_roles.
    allowed_roles: list of strings, e.g. ['admin', 'head']
    """
    init_session()
    if not st.session_state[SESSION_LOGGED_IN]:
        st.error("Please log in first.")
        st.stop()
    if st.session_state[SESSION_ROLE] not in allowed_roles:
        st.error(f"Access denied. You must be one of: {', '.join(allowed_roles)}")
        st.stop()

def login_student(student_id):
    """Validate student ID and set session state."""
    row = fetch_one("SELECT student_id, name FROM Student WHERE student_id = %s", (student_id,))
    if row:
        st.session_state[SESSION_LOGGED_IN] = True
        st.session_state[SESSION_ROLE] = 'student'
        st.session_state[SESSION_USER_ID] = row['student_id']
        st.session_state[SESSION_USER_NAME] = row['name']
        return True
    return False

def login_head(student_id):
    """Validate that student is a club head and set session state."""
    row = fetch_one(
        "SELECT s.student_id, s.name, cm.club_id FROM Student s "
        "JOIN Club_Memberships cm ON s.student_id = cm.student_id "
        "WHERE s.student_id = %s AND cm.role = %s",
        (student_id, 'Head')
    )
    if row:
        st.session_state[SESSION_LOGGED_IN] = True
        st.session_state[SESSION_ROLE] = 'head'
        st.session_state[SESSION_USER_ID] = row['student_id']
        st.session_state[SESSION_USER_NAME] = row['name']
        st.session_state[SESSION_CLUB_ID] = row['club_id']
        return True
    return False

def login_admin(admin_id):
    """Validate admin ID and set session state."""
    row = fetch_one("SELECT admin_id, name FROM Admin WHERE admin_id = %s", (admin_id,))
    if row:
        st.session_state[SESSION_LOGGED_IN] = True
        st.session_state[SESSION_ROLE] = 'admin'
        st.session_state[SESSION_USER_ID] = row['admin_id']
        st.session_state[SESSION_USER_NAME] = row['name']
        return True
    return False

def logout():
    """Clear session state."""
    for key in [SESSION_LOGGED_IN, SESSION_ROLE, SESSION_USER_ID, SESSION_USER_NAME, SESSION_CLUB_ID]:
        if key in st.session_state:
            del st.session_state[key]