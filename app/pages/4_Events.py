import streamlit as st
from datetime import date, datetime, time, timedelta
from auth import require_role
from constants import (
    SESSION_ROLE, SESSION_USER_ID, SESSION_CLUB_ID,
    SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN,
    EVENT_PARTICIPATION, EVENT_VIEW, EVENT_SCHEDULED, EVENT_CANCELLED,
)
from queries.common import get_club_by_id
from queries.event_queries import (
    list_upcoming_events, get_registrable_events, register_for_event,
    cancel_registration, get_my_events, create_event, cancel_event,
    get_club_events, get_event_participants,
)

require_role([SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD, SESSION_ROLE_ADMIN])
st.title("📅 Events")

role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]
club_id = st.session_state[SESSION_CLUB_ID]   # only set for a club head

# Show the result message from the previous action (we rerun after every change
# so that the tables below always show fresh data).
flash = st.session_state.pop("events_flash", None)
if flash:
    ok, msg = flash
    if ok:
        st.success(msg)
    else:
        st.error(msg)


def finish(result):
    st.session_state["events_flash"] = result
    st.rerun()


def fmt(moment):
    """Date and time as text, for the drop-down lists."""
    return moment.strftime("%d %b %Y, %I:%M %p")


# ---------------- Table layouts (column names come from the query functions) ----------------
DATE_FORMAT = "DD MMM YYYY, hh:mm a"
EVENT_COLUMNS = {
    "name": st.column_config.TextColumn("Event"),
    "club_name": st.column_config.TextColumn("Club"),
    "event_date": st.column_config.DatetimeColumn("Date & time", format=DATE_FORMAT),
    "venue": st.column_config.TextColumn("Venue"),
    "type": st.column_config.TextColumn("Type"),
    "status": st.column_config.TextColumn("Status"),
}
UPCOMING_COLUMNS = {**EVENT_COLUMNS, "description": st.column_config.TextColumn("Description")}
MY_EVENT_COLUMNS = {
    **EVENT_COLUMNS,
    "registered_at": st.column_config.DatetimeColumn("Registered on", format=DATE_FORMAT),
}
CLUB_EVENT_COLUMNS = {
    "name": st.column_config.TextColumn("Event"),
    "event_date": st.column_config.DatetimeColumn("Date & time", format=DATE_FORMAT),
    "venue": st.column_config.TextColumn("Venue"),
    "type": st.column_config.TextColumn("Type"),
    "status": st.column_config.TextColumn("Status"),
    "registrations": st.column_config.NumberColumn("Registrations"),
}
PARTICIPANT_COLUMNS = {
    "student_id": st.column_config.TextColumn("Student ID"),
    "name": st.column_config.TextColumn("Name"),
    "email_id": st.column_config.TextColumn("Email"),
    "department": st.column_config.TextColumn("Department"),
    "registered_at": st.column_config.DatetimeColumn("Registered on", format=DATE_FORMAT),
}


def show_table(rows, columns):
    st.dataframe(rows, hide_index=True, column_config=columns, column_order=list(columns))


# ---------------- Load the data this role needs ----------------
events = list_upcoming_events()
scheduled = [e for e in events if e["status"] == EVENT_SCHEDULED]
cancelled = [e for e in events if e["status"] == EVENT_CANCELLED]

# The admin is not a student, so there are no registrations to load
registrable, my_events, club_events = [], [], []
if role != SESSION_ROLE_ADMIN:
    registrable = get_registrable_events(user_id)
    my_events = get_my_events(user_id)
if role == SESSION_ROLE_HEAD:
    club_events = get_club_events(club_id)
my_upcoming = [e for e in my_events if e["is_upcoming"] and e["status"] == EVENT_SCHEDULED]

# ---------------- Metrics ----------------
if role == SESSION_ROLE_ADMIN:
    c1, c2 = st.columns(2)
    c1.metric("Upcoming events", len(scheduled))
    c2.metric("Cancelled events", len(cancelled))
elif role == SESSION_ROLE_HEAD:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Upcoming events", len(scheduled))
    c2.metric("Open for registration", len(registrable))
    c3.metric("My upcoming registrations", len(my_upcoming))
    c4.metric("My club's events", len(club_events))
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Upcoming events", len(scheduled))
    c2.metric("Open for registration", len(registrable))
    c3.metric("My upcoming registrations", len(my_upcoming))

# Admin: 1 tab (view only). Student: 3 tabs. Club head: 3 tabs + 2 more.
if role == SESSION_ROLE_ADMIN:
    tab_names = ["📋 Upcoming events"]
else:
    tab_names = ["📋 Upcoming events", "📝 Register", "🎟️ My events"]
    if role == SESSION_ROLE_HEAD:
        tab_names += ["➕ Create event", "🛠️ Manage events"]
tabs = st.tabs(tab_names)

# ---------------- Upcoming events ----------------
with tabs[0]:
    if not events:
        st.info("There are no upcoming events right now.")
    else:
        show_table(events, UPCOMING_COLUMNS)
        st.caption("Cancelled events stay in the list but cannot be registered for. "
                   "View events are open to watch and need no registration.")
    if role == SESSION_ROLE_ADMIN:
        st.info("Admins can only view events. A club head creates and cancels the events of their own club.")

# The admin can only view the events. Stop here so that the other tabs are not built.
if role == SESSION_ROLE_ADMIN:
    st.stop()

# ---------------- Register ----------------
with tabs[1]:
    if not registrable:
        st.info("There is no event you can register for right now.")
    else:
        labels = {e["event_id"]: f"{e['name']} · {e['club_name']} · {fmt(e['event_date'])}"
                  for e in registrable}
        with st.form("register_form"):
            event_id = st.selectbox("Choose an event", list(labels),
                                    format_func=lambda i: labels[i])
            if st.form_submit_button("Register"):
                finish(register_for_event(event_id, user_id))
    st.caption("Only Participation events that are Scheduled, in the future and not yet registered are listed.")

# ---------------- My events ----------------
with tabs[2]:
    if not my_events:
        st.info("You have not registered for any event yet. Open the **Register** tab.")
    else:
        show_table(my_events, MY_EVENT_COLUMNS)
        # Only events that have not happened yet can be cancelled; past ones stay as history.
        cancellable = {e["event_id"]: f"{e['name']} · {e['club_name']} · {fmt(e['event_date'])}"
                       for e in my_events if e["is_upcoming"]}
        if not cancellable:
            st.caption("Events that already took place stay in your history.")
        else:
            st.subheader("Cancel a registration")
            with st.form("cancel_registration_form"):
                event_id = st.selectbox("Choose a registration", list(cancellable),
                                        format_func=lambda i: cancellable[i], key="cancel_reg_pick")
                st.caption("Your registration is deleted. You can register again later if the event is still open.")
                if st.form_submit_button("Cancel registration"):
                    finish(cancel_registration(event_id, user_id))

# ---------------- Create event (club head only) ----------------
if role == SESSION_ROLE_HEAD:
    with tabs[3]:
        st.subheader("Create an event for " + get_club_by_id(club_id)["club_name"])
        with st.form("create_event_form", clear_on_submit=True):
            name = st.text_input("Event name")
            description = st.text_area("Description")
            col1, col2 = st.columns(2)
            event_day = col1.date_input("Date", value=date.today() + timedelta(days=7),
                                        min_value=date.today())
            event_time = col2.time_input("Time", value=time(10, 0))
            venue = st.text_input("Venue")
            event_type = st.selectbox("Event type", [EVENT_PARTICIPATION, EVENT_VIEW])
            st.caption("Participation: students can register. View: students only come and watch.")
            if st.form_submit_button("Create event"):
                finish(create_event(club_id, name, description,
                                    datetime.combine(event_day, event_time), venue, event_type))

# ---------------- Manage events (club head only) ----------------
if role == SESSION_ROLE_HEAD:
    with tabs[4]:
        if not club_events:
            st.info("Your club has not created any event yet.")
        else:
            show_table(club_events, CLUB_EVENT_COLUMNS)

            names = {e["event_id"]: f"{e['name']} ({fmt(e['event_date'])}) · {e['status']}"
                     for e in club_events}
            event_id = st.selectbox("Choose an event", list(names),
                                    format_func=lambda i: names[i], key="manage_pick")
            chosen = next(e for e in club_events if e["event_id"] == event_id)

            participants = get_event_participants(event_id)
            st.subheader(f"Registered students ({len(participants)})")
            if not participants:
                st.info("Nobody has registered for this event.")
            else:
                show_table(participants, PARTICIPANT_COLUMNS)

            # Only a Scheduled event can be cancelled. The row is kept, never deleted.
            if chosen["status"] == EVENT_CANCELLED:
                st.caption("This event is already cancelled.")
            else:
                with st.form("cancel_event_form"):
                    st.caption("The event stays in the list, marked Cancelled. "
                               "Nobody can register for it any more, and this cannot be undone.")
                    confirm = st.checkbox("I confirm that I want to cancel this event")
                    if st.form_submit_button("Cancel event"):
                        if not confirm:
                            st.error("Tick the confirmation box first.")
                        else:
                            finish(cancel_event(event_id, club_id))