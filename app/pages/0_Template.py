import streamlit as st
from auth import require_role, init_session
from constants import SESSION_ROLE, SESSION_USER_ID, SESSION_CLUB_ID
from queries.common import get_clubs_of_student, get_head_club

init_session()
require_role(['student'])  # CHANGE THIS FOR YOUR PAGE

st.title("📋 Example Page")

role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]

if role == 'student':
    st.write("Hello, this is a student-only page.")
    
    clubs = get_clubs_of_student(user_id)
    st.write(f"You are a member of {len(clubs)} club(s).")
    
    for club in clubs:
        st.write(f"- {club['club_name']} ({club['role']})")

elif role == 'head':
    st.write("Hello, this is a head-only page.")
    club = get_head_club(user_id)
    st.write(f"You head: {club['club_name']}")

elif role == 'admin':
    st.write("Hello, this is an admin-only page.")