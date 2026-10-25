import streamlit as st
from database import get_connection

st.title("🎓 Campus Club & Event Management System")

# Simple Role Selection & ID Login based
role = st.sidebar.selectbox("Select Role", ["Student", "Club Manager / Head", "Admin"])
user_id = st.sidebar.text_input("Enter ID Number (e.g., CS25B1024 or Admin ID)")

if user_id:
    conn = get_connection()
    cursor = conn.cursor()
    
    if role == "Student":
        cursor.execute("SELECT * FROM Student WHERE student_id = %s;", (user_id,))
        user = cursor.fetchone()
        if user:
            st.success(f"Welcome, {user[1]} ({user[3]})!")
            st.info("Navigate to student features: View Club Statistics, Apply for Recruitment, Register for Events.")
        else:
            st.error("Student ID not found!")
            
    elif role == "Club Manager / Head":
        cursor.execute("SELECT * FROM Club_Memberships WHERE student_id = %s AND role = 'Head';", (user_id,))
        head_check = cursor.fetchone()
        if head_check:
            st.success("Club Head Dashboard Active")
            st.info("Manage club members, post recruitment drives, and organize events.")
        else:
            st.error("Access Denied: You are not registered as a Club Head.")
            
    elif role == "Admin":
        cursor.execute("SELECT * FROM Admin WHERE admin_id::text = %s;", (user_id,))
        admin_check = cursor.fetchone()
        if admin_check:
            st.success(f"Welcome Admin: {admin_check[1]}")
            st.info("Manage clubs, assign heads, and oversee system operations.")
        else:
            st.error("Admin ID not found!")
            
    cursor.close()
    conn.close()