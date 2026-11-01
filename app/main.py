# Router: decides which pages the logged-in user can see.
import streamlit as st
from auth import init_session
from constants import SESSION_LOGGED_IN, SESSION_ROLE, SESSION_ROLE_ADMIN
from ui import inject_css, render_sidebar_user

st.set_page_config(page_title="Campus Club Hub", page_icon="🎓", layout="wide")
init_session()
inject_css()

logged_in = st.session_state[SESSION_LOGGED_IN]

if not logged_in:
    # Not logged in: the only page is the login page
    navigation = st.navigation([st.Page("login.py", title="Login", icon="🔐")])
else:
    home = st.Page("home.py", title="Home", icon="🏠", default=True)
    recruitment = st.Page("pages/2_Recruitment.py", title="Recruitment", icon="📝")
    members = st.Page("pages/3_Members.py", title="Club Members", icon="👥")
    events = st.Page("pages/4_Events.py", title="Events", icon="📅")
    stats = st.Page("pages/5_Club_Stats.py", title="Club Statistics", icon="📊")

    if st.session_state[SESSION_ROLE] == SESSION_ROLE_ADMIN:
        admin_clubs = st.Page("pages/1_Admin_Clubs.py", title="Manage clubs", icon="🛠️")
        menu = {
            "Main": [home],
            "Administration": [admin_clubs],
            "Browse": [recruitment, members, events, stats],
        }
    else:
        menu = {
            "Main": [home],
            "Clubs": [recruitment, members],
            "Events": [events, stats],
        }
    navigation = st.navigation(menu)

# IMPORTANT: draw the sidebar user card AFTER st.navigation() has chosen the page.
# If a button is created before it, its id changes after login and the first click is lost.
if logged_in:
    render_sidebar_user()

navigation.run()