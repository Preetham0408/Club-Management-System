import streamlit as st
from auth import require_role
from constants import SESSION_ROLE_ADMIN,SESSION_ROLE_STUDENT,SESSION_ROLE_HEAD
require_role([SESSION_ROLE_ADMIN,SESSION_ROLE_STUDENT,SESSION_ROLE_HEAD])
st.title("roles: student+ head + admin")
st.info("Owner: Person C. Not built yet.")