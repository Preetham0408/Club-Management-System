import streamlit as st
from datetime import date, timedelta
from auth import require_role
from constants import (
    SESSION_ROLE, SESSION_USER_ID, SESSION_CLUB_ID,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN, STATUS_PENDING,
)
from queries.recruitment_queries import (
    get_open_drives, get_club_drives, get_drive_applications, get_my_applications,
    create_drive, apply_to_drive, select_application, reject_application,
)

require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN])
st.title("📝 Recruitment")

role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]
club_id = st.session_state[SESSION_CLUB_ID]   # only set for a club head

# Show the result message from the previous action (we rerun after every change
# so that the tables below always show fresh data).
flash = st.session_state.pop("recruit_flash", None)
if flash:
    ok, msg = flash
    if ok:
        st.success(msg)
    else:
        st.error(msg)


def finish(result):
    st.session_state["recruit_flash"] = result
    st.rerun()


# Admin: 1 tab (view only). Student: 3 tabs. Club head: 3 tabs + 2 more.
if role == SESSION_ROLE_ADMIN:
    tab_names = ["📋 Open drives"]
else:
    tab_names = ["📋 Open drives", "📝 Apply", "📄 My applications"]
    if role == SESSION_ROLE_HEAD:
        tab_names += ["➕ Post drive", "✅ Review applications"]
tabs = st.tabs(tab_names)

drives = get_open_drives()
# The admin is not a student, so there are no applications to load
my_applications = [] if role == SESSION_ROLE_ADMIN else get_my_applications(user_id)

# ---------------- Open drives ----------------
with tabs[0]:
    if role == SESSION_ROLE_ADMIN:
        st.metric("Open drives", len(drives))
    else:
        c1, c2 = st.columns(2)
        c1.metric("Open drives", len(drives))
        c2.metric("My applications", len(my_applications))
    if not drives:
        st.info("There are no open recruitment drives right now.")
    else:
        st.dataframe(drives)
    
# The admin can only view the drives. Stop here so that the Apply
if role == SESSION_ROLE_ADMIN:
    st.stop()

# ---------------- Apply ----------------
with tabs[1]:
    if not drives:
        st.info("There are no open recruitment drives right now.")
    else:
        labels = {d["rec_id"]: f"{d['club_name']} (apply by {d['ends_on']})" for d in drives}
        with st.form("apply_form"):
            rec_id = st.selectbox("Choose a drive", list(labels),
                                  format_func=lambda i: labels[i])
            if st.form_submit_button("Apply"):
                finish(apply_to_drive(rec_id, user_id))

# ---------------- My applications ----------------
with tabs[2]:
    if not my_applications:
        st.info("You have not applied to any drive yet.")
    else:
        st.dataframe(my_applications)

# ---------------- Post drive (head only) ----------------
if role == SESSION_ROLE_HEAD:
    with tabs[3]:
        with st.form("post_drive_form", clear_on_submit=True):
            ends_on = st.date_input("Last date to apply",
                                    value=date.today() + timedelta(days=14),
                                    min_value=date.today())
            description = st.text_area("Description")
            if st.form_submit_button("Post drive"):
                finish(create_drive(club_id, ends_on, description))

# ---------------- Review applications (head only) ----------------
if role == SESSION_ROLE_HEAD:
    with tabs[4]:
        club_drives = get_club_drives(club_id)
        if not club_drives:
            st.info("Your club has not posted any drive yet.")
        else:
            names = {d["rec_id"]: f"{d['description']} (ends {d['ends_on']})" for d in club_drives}
            rec_id = st.selectbox("Choose a drive", list(names),
                                  format_func=lambda i: names[i], key="review_pick")
            applications = get_drive_applications(rec_id)
            if not applications:
                st.info("No applications for this drive yet.")
            else:
                st.dataframe(applications)

            # Only Pending applications can be decided
            pending = {a["application_id"]: a for a in applications if a["status"] == STATUS_PENDING}
            if pending:
                with st.form("review_form"):
                    app_id = st.selectbox("Pending applicant", list(pending),
                                          format_func=lambda i: f"{pending[i]['name']} ({pending[i]['student_id']})")
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("✅ Select"):
                        finish(select_application(app_id, club_id, pending[app_id]["student_id"]))
                    if col2.form_submit_button("❌ Reject"):
                        finish(reject_application(app_id))