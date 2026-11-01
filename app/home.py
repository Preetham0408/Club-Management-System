import streamlit as st
from auth import require_role
from constants import (
    SESSION_ROLE, SESSION_USER_ID, SESSION_USER_NAME, SESSION_CLUB_ID,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN,
)
from queries.common import get_club_by_id, get_clubs_of_student
from queries.club_queries import (
    get_system_overview, get_clubs_overview, get_head_dashboard, get_student_dashboard,
)

require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN])

role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]
st.title(f"👋 Welcome, {st.session_state[SESSION_USER_NAME]}")

# ---------------- Admin ----------------
if role == SESSION_ROLE_ADMIN:
    st.caption("Administrator dashboard")
    o = get_system_overview()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Students", o["students"])
    c2.metric("Clubs", o["clubs"])
    c3.metric("Open drives", o["open_drives"])
    c4.metric("Upcoming events", o["upcoming_events"])
    c5.metric("Pending applications", o["pending_applications"])

    st.subheader("Clubs at a glance")
    st.dataframe(get_clubs_overview(), hide_index=True)
    st.info("Open **Manage clubs** in the sidebar to create, rename or delete clubs and change heads.")

# ---------------- Club head / Student ----------------
else:
    if role == SESSION_ROLE_HEAD:
        club = get_club_by_id(st.session_state[SESSION_CLUB_ID])
        st.caption(f"Head of {club['club_name']}")
        d = get_head_dashboard(club["club_id"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Members", d["members"])
        c2.metric("Open drives", d["open_drives"])
        c3.metric("Pending applications", d["pending_applications"])
        c4.metric("Upcoming events", d["upcoming_events"])
        if d["pending_applications"] > 0:
            st.warning(f"You have {d['pending_applications']} pending application(s). "
                       "Open **Recruitment → Review applications** to decide.")
    else:
        st.caption("Student dashboard")
        d = get_student_dashboard(user_id)
        c1, c2, c3 = st.columns(3)
        c1.metric("My clubs", d["my_clubs"])
        c2.metric("Pending applications", d["pending_applications"])
        c3.metric("Events I registered for", d["upcoming_registrations"])

    st.subheader("My clubs")
    my_clubs = get_clubs_of_student(user_id)
    if my_clubs:
        st.dataframe(my_clubs, hide_index=True)
    else:
        st.info("You have not joined any club yet. Open **Recruitment** to apply.")