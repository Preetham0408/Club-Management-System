import streamlit as st
from auth import init_session, login_student, login_head, login_admin, logout, require_role
from constants import SESSION_LOGGED_IN, SESSION_ROLE, SESSION_USER_NAME

st.set_page_config(page_title="Club Management System", layout="wide")

init_session()

# If already logged in, show home page
if st.session_state[SESSION_LOGGED_IN]:
    st.title(f"🎓 Welcome, {st.session_state[SESSION_USER_NAME]}!")
    st.info(f"**Role:** {st.session_state[SESSION_ROLE].upper()}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state[SESSION_ROLE] == 'student':
            st.write("""
            ### Student Features (see left sidebar)
            - Browse and register for events
            - Apply for club recruitment
            - View club statistics
            """)
        elif st.session_state[SESSION_ROLE] == 'head':
            st.write("""
            ### Club Head Features (see left sidebar)
            - Manage club members
            - Post recruitment drives
            - Create and manage events
            """)
        elif st.session_state[SESSION_ROLE] == 'admin':
            st.write("""
            ### Admin Features (see left sidebar)
            - Create and manage clubs
            - Assign club heads
            - Oversee system operations
            """)
    
    with col2:
        if st.button("🚪 Logout", key="main_logout"):
            logout()
            st.rerun()
else:
    # Login form
    st.title("🎓 Campus Club & Event Management System")
    
    role = st.selectbox("Select your role:", 
                        ["Student", "Club Head", "Admin"],
                        key="login_role")
    user_id = st.text_input("Enter your ID:", key="login_id")
    
    if st.button("Login"):
        success = False
        if role == "Student":
            success = login_student(user_id)
            error_msg = "Student ID not found."
        elif role == "Club Head":
            success = login_head(user_id)
            error_msg = "Either this student ID doesn't exist, or this student is not a club head."
        elif role == "Admin":
            success = login_admin(user_id)
            error_msg = "Admin ID not found."
        
        if success:
            st.success(f"Welcome! Redirecting...")
            st.rerun()
        else:
            st.error(error_msg)
    
    # Show test credentials
    with st.expander("📋 Test Credentials (for development)"):
        st.write("""
        **Students:** CS25B1019, CS25B1002, CS25B1051, CS25B1047
        
        **Club Heads:** CS25B1019 (Developer Club), CS25B1002 (Robotics Club)
        
        **Admins:** 1, 2
        """)