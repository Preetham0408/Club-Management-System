import streamlit as st
from auth import require_role
from constants import SESSION_CLUB_ID, SESSION_ROLE_HEAD
from queries.common import get_club_by_id, get_club_members
from queries.recruitment_queries import remove_member

require_role([SESSION_ROLE_HEAD])

club_id = st.session_state[SESSION_CLUB_ID]
club = get_club_by_id(club_id)
st.title("👥 Members of " + club["club_name"])

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


members = get_club_members(club_id)
tab_list, tab_remove = st.tabs(["👥 Member list", "🗑️ Remove member"])

# ---------------- Member list ----------------
with tab_list:
    st.metric("Total members", len(members))
    st.dataframe(members)

# ---------------- Remove member ----------------
with tab_remove:
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