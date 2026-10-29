import streamlit as st
from auth import require_role
from constants import SESSION_ROLE_ADMIN
require_role([SESSION_ROLE_ADMIN])
st.title("roles: admin")
st.info("Owner: Person A. Not built yet.")