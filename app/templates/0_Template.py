import streamlit as st
from auth import require_role
from constants import SESSION_ROLE, SESSION_USER_ID, SESSION_CLUB_ID, SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD
from queries.common import get_clubs_of_student

# 1. Who may open this page
require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD])

st.title("Page title here")

# 2. Who is logged in
role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]

# 3. Call query functions. Never write SQL in a page file.
if role == SESSION_ROLE_HEAD:
    st.subheader("Head view")
    st.write(f"Your club id: {st.session_state[SESSION_CLUB_ID]}")
else:
    st.subheader("Student view")

clubs = get_clubs_of_student(user_id)
st.write(f"You belong to {len(clubs)} club(s).")
for club in clubs:
    st.write(f"- {club['club_name']} ({club['role']})")