import streamlit as st
from auth import require_role
from constants import SESSION_ROLE_ADMIN,SESSION_ROLE_STUDENT,SESSION_ROLE_HEAD
require_role([SESSION_ROLE_ADMIN,SESSION_ROLE_STUDENT,SESSION_ROLE_HEAD])
st.title("roles: head + students (view only access)")
st.info("Owner: Person B. Not built yet.")