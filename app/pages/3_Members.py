import streamlit as st
from auth import require_role
from constants import (
    SESSION_ROLE, SESSION_CLUB_ID,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN,
)
from queries.common import get_all_clubs, get_club_by_id, get_club_members
from queries.recruitment_queries import remove_member

require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN])

role = st.session_state[SESSION_ROLE]
club_id = st.session_state[SESSION_CLUB_ID]   # only set for a club head
st.title("👥 Club members")

# Show the result message from the previous action (we rerun after every change
# so that the tables below always show fresh data).
flash = st.session_state.pop("members_flash", None)
if flash:
    ok, msg = flash
    if ok:
        st.success(msg)
    else:
        st.error(msg)


def finish(result):
    st.session_state["members_flash"] = result
    st.rerun()


# ---------------- Tabs ----------------
# Everyone sees the list of clubs. Only a club head also gets "Remove member".
tab_names = ["🏛️ All clubs"]
if role == SESSION_ROLE_HEAD:
    tab_names.append("🗑️ Remove member")
tabs = st.tabs(tab_names)

# ---------------- All clubs: expand a club to see its members ----------------
with tabs[0]:
    clubs = get_all_clubs()
    if not clubs:
        st.info("There are no clubs yet.")
    for club in clubs:
        club_members = get_club_members(club["club_id"])   # Head first, then Members A-Z
        with st.expander(f"{club['club_name']}  ({len(club_members)} members)"):
            if not club_members:
                st.write("No members yet.")
            else:
                st.dataframe(club_members, hide_index=True)

# ---------------- Remove member (club head only) ----------------
if role == SESSION_ROLE_HEAD:
    with tabs[1]:
        my_club = get_club_by_id(club_id)
        st.subheader("Remove a member from " + my_club["club_name"])
        members = get_club_members(club_id)
        names = {m["student_id"]: f"{m['student_id']} - {m['name']} ({m['role']})" for m in members}
        with st.form("remove_form"):
            student_id = st.selectbox("Choose a person", list(names), format_func=lambda i: names[i])
            st.caption("The club head cannot be removed.")
            confirm = st.checkbox("I confirm that I want to remove this person")
            if st.form_submit_button("Remove"):
                if not confirm:
                    st.error("Tick the confirmation box first.")
                else:
                    finish(remove_member(club_id, student_id))