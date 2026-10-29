import streamlit as st
from auth import init_session, login_student, login_head, login_admin, logout
from constants import SESSION_LOGGED_IN, SESSION_ROLE, SESSION_USER_NAME

st.set_page_config(page_title="Club Management System", layout="wide")
init_session()

if st.session_state[SESSION_LOGGED_IN]:
    st.title(f"🎓 Welcome, {st.session_state[SESSION_USER_NAME]}!")
    st.info(f"Logged in as: {st.session_state[SESSION_ROLE]}")
    st.write("Use the left sidebar to open the pages for your role.")
    if st.button("🚪 Logout"):
        logout()
        st.rerun()
else:
    st.title("🎓 Campus Club & Event Management System")
    role_choice = st.selectbox("Select your role:", ["Student", "Club Head", "Admin"], key="login_role")
    user_id = st.text_input("Enter your ID:", key="login_id").strip()

    if st.button("Login"):
        if role_choice == "Student":
            ok = login_student(user_id.upper())
            msg = "Student ID not found."
        elif role_choice == "Club Head":
            ok = login_head(user_id.upper())
            msg = "This ID is not a club head (or does not exist)."
        else:
            ok = user_id.isdigit() and login_admin(int(user_id))
            msg = "Admin ID must be a number that exists (e.g. 1)."

        if ok:
            st.rerun()
        else:
            st.error(msg)

    with st.expander("📋 Test credentials (remove before final submission)"):
        st.write("""
        **Students:** CS25B1019, CS25B1002, CS25B1051, CS25B1047
        **Club Heads:** CS25B1019 (Developer Club), CS25B1002 (Robotics Club)
        **Admins:** 1, 2
        """)