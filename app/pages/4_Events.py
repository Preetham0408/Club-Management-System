import streamlit as st
from datetime import date, datetime, time, timedelta

from auth import require_role
from constants import (
    SESSION_ROLE,
    SESSION_ROLE_ADMIN,
    SESSION_ROLE_STUDENT,
    SESSION_ROLE_HEAD,
    SESSION_USER_ID,
    SESSION_USER_NAME,
    SESSION_CLUB_ID,
    EVENT_PARTICIPATION,
    EVENT_VIEW,
    EVENT_SCHEDULED,
    EVENT_CANCELLED,
)
from queries.event_queries import (
    list_upcoming_events,
    register_for_event,
    cancel_registration,
    get_my_events,
    create_event,
    cancel_event,
    get_event_participants,
)

# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

require_role([
    SESSION_ROLE_ADMIN,
    SESSION_ROLE_STUDENT,
    SESSION_ROLE_HEAD,
])

user_role = st.session_state[SESSION_ROLE]
user_id = st.session_state[SESSION_USER_ID]
user_name = st.session_state[SESSION_USER_NAME]
head_club_id = st.session_state[SESSION_CLUB_ID]

st.title("Events")
st.write(f"Welcome, **{user_name}**")

# Fetch events and registrations
events = list_upcoming_events()

my_events = []
registered_event_ids = set()

if user_role in (SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD):
    my_events = get_my_events(user_id)
    registered_event_ids = {
        event["event_id"] for event in my_events
    }


# --------------------------------------------------
# 1. DISPLAY UPCOMING EVENTS
# --------------------------------------------------

st.header("Upcoming Events")

if not events:
    st.info("There are no upcoming events.")
else:
    for event in events:
        event_id = event["event_id"]
        event_type = event["type"]
        event_status = event["status"]

        with st.container(border=True):
            st.subheader(event["name"])

            st.write(f"**Club:** {event['club_name']}")
            st.write(
                f"**Date:** {event['event_date'].strftime('%d %B %Y, %I:%M %p')}"
            )
            st.write(f"**Venue:** {event['venue']}")
            st.write(f"**Type:** {event_type}")

            if event["description"]:
                st.write(event["description"])

            if event_status == EVENT_CANCELLED:
                st.error("Cancelled")
            else:
                st.success("Scheduled")

            if user_role in (SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD):

                if event_status == EVENT_CANCELLED:
                    st.warning("Registration is unavailable for this event.")

                elif event_type == EVENT_VIEW:
                    st.info("View-only event. Registration is not required.")

                elif event_id in registered_event_ids:
                    st.success("Already Registered")

                elif (
                    event_type == EVENT_PARTICIPATION
                    and event_status == EVENT_SCHEDULED
                    and event["event_date"] > datetime.now()
                ):
                    if st.button(
                        "Register",
                        key=f"register_{event_id}",
                    ):
                        success, message = register_for_event(
                            event_id,
                            user_id,
                        )

                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                        st.rerun()


# --------------------------------------------------
# 2. MY REGISTERED EVENTS
# --------------------------------------------------

if user_role in (SESSION_ROLE_STUDENT, SESSION_ROLE_HEAD):

    st.divider()
    st.header("My Registered Events")

    if not my_events:
        st.info("You have not registered for any events.")

    else:
        for event in my_events:
            event_id = event["event_id"]

            with st.container(border=True):
                st.subheader(event["name"])

                st.write(f"**Club:** {event['club_name']}")
                st.write(
                    f"**Date:** {event['event_date'].strftime('%d %B %Y, %I:%M %p')}"
                )
                st.write(f"**Venue:** {event['venue']}")

                if event["status"] == EVENT_CANCELLED:
                    st.error("This event has been cancelled.")
                else:
                    st.success("Registration active")

                if st.button(
                    "Cancel My Registration",
                    key=f"cancel_registration_{event_id}",
                ):
                    success, message = cancel_registration(
                        event_id,
                        user_id,
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                    st.rerun()


# --------------------------------------------------
# 3. CLUB HEAD EVENT MANAGEMENT
# --------------------------------------------------

if user_role == SESSION_ROLE_HEAD:

    st.divider()
    st.header("Club Head: Manage Your Events")

    st.write(f"Your Club ID: **{head_club_id}**")

    # CREATE EVENT
    st.subheader("Create New Event")

    with st.form("create_event_form"):

        event_name = st.text_input("Event Name")

        event_description = st.text_area("Description")

        event_date = st.date_input(
            "Event Date",
            value=date.today() + timedelta(days=1),
            min_value=date.today(),
        )

        event_time = st.time_input(
            "Event Time",
            value=time(9, 0),
        )

        event_venue = st.text_input("Venue")

        event_type = st.selectbox(
            "Event Type",
            options=[EVENT_PARTICIPATION, EVENT_VIEW],
        )

        submitted = st.form_submit_button("Create Event")

        if submitted:

            if not event_name.strip():
                st.error("Event name is required.")

            elif not event_venue.strip():
                st.error("Venue is required.")

            else:
                combined_datetime = datetime.combine(
                    event_date,
                    event_time,
                )

                if combined_datetime <= datetime.now():
                    st.error("Choose a future date and time.")

                else:
                    success, message = create_event(
                        head_club_id,
                        event_name.strip(),
                        event_description.strip(),
                        combined_datetime,
                        event_venue.strip(),
                        event_type,
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                    st.rerun()

    # MANAGE OWN CLUB EVENTS
    st.divider()
    st.subheader("Your Club's Upcoming Events")

    own_events = [
        event
        for event in events
        if event["club_id"] == head_club_id
    ]

    if not own_events:
        st.info("Your club has no upcoming events.")

    else:
        for event in own_events:

            event_id = event["event_id"]

            with st.expander(
                f"{event['name']} — {event['status']}"
            ):

                st.write(f"**Date:** {event['event_date']}")
                st.write(f"**Venue:** {event['venue']}")
                st.write(f"**Type:** {event['type']}")
                st.write(event["description"] or "No description.")

                # PARTICIPANT LIST
                participants = get_event_participants(event_id)

                st.write(
                    f"**Registered Participants:** {len(participants)}"
                )

                if participants:
                    st.dataframe(
                        [dict(student) for student in participants],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No registrations yet.")

                # CANCEL EVENT
                if event["status"] != EVENT_CANCELLED:

                    if st.button(
                        "Cancel This Event",
                        key=f"cancel_event_{event_id}",
                    ):
                        success, message = cancel_event(
                            event_id,
                            head_club_id,
                        )

                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                        st.rerun()


# --------------------------------------------------
# 4. ADMIN INFORMATION
# --------------------------------------------------

if user_role == SESSION_ROLE_ADMIN:

    st.divider()

    st.info(
        "Administrators have read-only access to events. "
        "Only Club Heads can create or cancel events."
    )
