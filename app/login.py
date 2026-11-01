import streamlit as st
from auth import login, login_student, login_head, login_admin
from constants import LOGIN_STUDENT, LOGIN_HEAD, LOGIN_ADMIN, SHOW_DEMO_LOGINS
from database import is_database_available
from queries.common import get_demo_accounts

# Friendly message instead of a long error if PostgreSQL / .env is wrong
if not is_database_available():
    st.error("Cannot connect to the database.")
    st.write("Check that PostgreSQL is running and that your `.env` file has the correct "
             "`DB_PASSWORD`, then refresh this page.")
    st.stop()

HINTS = {
    LOGIN_STUDENT: ("Student ID", "e.g. CS25B1019"),
    LOGIN_HEAD: ("Student ID of the club head", "e.g. CS25B1002"),
    LOGIN_ADMIN: ("Admin ID (a number)", "e.g. 1"),
}

_, middle, _ = st.columns([1, 1.6, 1])
with middle:
    st.markdown(
        '<div class="hero"><h1>🎓 Campus Club Hub</h1>'
        "<p>Clubs · Recruitment · Events</p></div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("Sign in")
        role_choice = st.radio("I am a", [LOGIN_STUDENT, LOGIN_HEAD, LOGIN_ADMIN],
                               horizontal=True, key="login_role")
        label, placeholder = HINTS[role_choice]
        with st.form("login_form"):      # a form lets the Enter key submit
            user_id = st.text_input(label, placeholder=placeholder)
            submitted = st.form_submit_button("Sign in", type="primary")
        if submitted:
            ok, msg = login(role_choice, user_id)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    if SHOW_DEMO_LOGINS:
        with st.expander("🧪 Demo accounts (for testing and the viva)"):
            st.caption("Click a name to sign in instantly. "
                       "Set SHOW_DEMO_LOGINS = False in constants.py before the final submission.")
            demo = get_demo_accounts()

            st.markdown("**Admin**")
            for a in demo["admins"]:
                if st.button(f"{a['name']} (ID {a['id']})", key=f"demo_admin_{a['id']}"):
                    login_admin(a["id"])
                    st.rerun()

            st.markdown("**Club Head**")
            for h in demo["heads"]:
                if st.button(f"{h['name']} · {h['club_name']} ({h['id']})", key=f"demo_head_{h['id']}"):
                    login_head(h["id"])
                    st.rerun()

            st.markdown("**Student**")
            for s in demo["students"]:
                if st.button(f"{s['name']} ({s['id']})", key=f"demo_student_{s['id']}"):
                    login_student(s["id"])
                    st.rerun()