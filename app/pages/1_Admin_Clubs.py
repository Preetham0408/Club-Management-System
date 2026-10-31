import streamlit as st
from auth import require_role
from constants import SESSION_ROLE_ADMIN
from queries.common import get_all_clubs, get_club_members, get_club_head
from queries.club_queries import (
    get_system_overview, get_clubs_overview, get_all_admins,
    get_students_available_as_head, get_club_deletion_impact,
    create_club, rename_club, assign_head, delete_club,
)

require_role([SESSION_ROLE_ADMIN])
st.title("🛠️ Admin: Club Management")

# Show the result message from the previous action (we rerun after every change
# so that the tables below always show fresh data).
flash = st.session_state.pop("admin_flash", None)
if flash:
    ok, msg = flash
    if ok:
        st.success(msg)
    else:
        st.error(msg)


def finish(result):
    st.session_state["admin_flash"] = result
    st.rerun()


tab_overview, tab_create, tab_rename, tab_head, tab_delete = st.tabs(
    ["📊 Overview", "➕ Create club", "✏️ Rename club", "👑 Change head", "🗑️ Delete club"]
)

# ---------------- Overview ----------------
with tab_overview:
    o = get_system_overview()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Students", o["students"])
    c2.metric("Clubs", o["clubs"])
    c3.metric("Open drives", o["open_drives"])
    c4.metric("Upcoming events", o["upcoming_events"])
    c5.metric("Pending applications", o["pending_applications"])

    st.subheader("All clubs")
    st.dataframe(get_clubs_overview())

    st.subheader("Members of each club")
    for club in get_all_clubs():
        with st.expander(club["club_name"]):
            st.dataframe(get_club_members(club["club_id"]))

# ---------------- Create ----------------
with tab_create:
    admins = get_all_admins()
    candidates = get_students_available_as_head()
    if not admins:
        st.warning("There are no admins in the database.")
    elif not candidates:
        st.warning("Every student already heads a club. A new club needs a free student as head.")
    else:
        admin_names = {a["admin_id"]: a["name"] for a in admins}
        student_names = {s["student_id"]: s["name"] for s in candidates}
        with st.form("create_club_form", clear_on_submit=True):
            name = st.text_input("Club name")
            email = st.text_input("Club email")
            admin_id = st.selectbox("Faculty admin in charge", list(admin_names),
                                    format_func=lambda i: f"{admin_names[i]} (ID {i})")
            head_id = st.selectbox("Club head (student)", list(student_names),
                                   format_func=lambda i: f"{i} - {student_names[i]}")
            if st.form_submit_button("Create club"):
                finish(create_club(name, email, admin_id, head_id))

# ---------------- Rename ----------------
with tab_rename:
    clubs = get_all_clubs()
    if not clubs:
        st.info("No clubs yet.")
    else:
        names = {c["club_id"]: c["club_name"] for c in clubs}
        club_id = st.selectbox("Choose a club", list(names),
                               format_func=lambda i: names[i], key="rename_pick")
        with st.form("rename_form"):
            new_name = st.text_input("New club name", value=names[club_id])
            if st.form_submit_button("Rename"):
                finish(rename_club(club_id, new_name))

# ---------------- Change head ----------------
with tab_head:
    clubs = get_all_clubs()
    candidates = get_students_available_as_head()
    if not clubs:
        st.info("No clubs yet.")
    elif not candidates:
        st.warning("No free student available. Every student already heads a club.")
    else:
        names = {c["club_id"]: c["club_name"] for c in clubs}
        club_id = st.selectbox("Choose a club", list(names),
                               format_func=lambda i: names[i], key="head_pick")
        current = get_club_head(club_id)
        st.write("Current head: " + (f"**{current['name']}** ({current['student_id']})" if current else "none"))
        student_names = {s["student_id"]: s["name"] for s in candidates}
        with st.form("head_form"):
            new_head = st.selectbox("New head", list(student_names),
                                    format_func=lambda i: f"{i} - {student_names[i]}")
            st.caption("The old head stays in the club as a Member.")
            if st.form_submit_button("Assign head"):
                finish(assign_head(club_id, new_head))

# ---------------- Delete ----------------
with tab_delete:
    clubs = get_all_clubs()
    if not clubs:
        st.info("No clubs yet.")
    else:
        names = {c["club_id"]: c["club_name"] for c in clubs}
        club_id = st.selectbox("Choose a club", list(names),
                               format_func=lambda i: names[i], key="delete_pick")
        impact = get_club_deletion_impact(club_id)
        st.warning(
            f"Deleting **{names[club_id]}** will also permanently delete: "
            f"{impact['memberships']} membership(s), {impact['events']} event(s), "
            f"{impact['drives']} recruitment drive(s) and {impact['applications']} application(s)."
        )
        with st.form("delete_form"):
            confirm = st.checkbox("I understand this cannot be undone")
            if st.form_submit_button("Delete club permanently"):
                if not confirm:
                    st.error("Tick the confirmation box first.")
                else:
                    finish(delete_club(club_id))