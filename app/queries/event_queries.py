
# Owner: Person C
# All SQL functions for the Events and Analytics module.

from database import fetch_all, fetch_one, execute
from constants import (
    EVENT_PARTICIPATION,
    EVENT_VIEW,
    EVENT_SCHEDULED,
    EVENT_CANCELLED,
)


def list_upcoming_events():
    """Return future events, including cancelled events for display."""
    return fetch_all(
        """
        SELECT
            e.event_id,
            e.club_id,
            c.club_name,
            e.name,
            e.description,
            e.event_date,
            e.venue,
            e.type,
            e.status
        FROM Events e
        JOIN Club c ON e.club_id = c.club_id
        WHERE e.event_date >= CURRENT_TIMESTAMP
        ORDER BY e.event_date ASC
        """
    )


def register_for_event(event_id, student_id):
    """
    Register a student for a valid Participation event.
    Returns (True, message) or (False, reason).
    """

    event = fetch_one(
        """
        SELECT
            event_id,
            type,
            status,
            event_date > CURRENT_TIMESTAMP AS is_future
        FROM Events
        WHERE event_id = %s
        """,
        (event_id,)
    )

    if event is None:
        return False, "Event does not exist."

    if event["type"] != EVENT_PARTICIPATION:
        return False, "You cannot register for a View event."

    if event["status"] != EVENT_SCHEDULED:
        return False, "This event is cancelled or not available."

    if not event["is_future"]:
        return False, "Registration is not allowed for past events."

    student = fetch_one(
        "SELECT student_id FROM Student WHERE student_id = %s",
        (student_id,)
    )

    if student is None:
        return False, "Student does not exist."

    existing = fetch_one(
        """
        SELECT participation_id
        FROM Event_Participation
        WHERE event_id = %s AND student_id = %s
        """,
        (event_id, student_id)
    )

    if existing is not None:
        return False, "You are already registered for this event."

    # Recheck eligibility in the INSERT to avoid inserting
    # if the event becomes unavailable between validation and insertion.
    inserted = execute(
        """
        INSERT INTO Event_Participation (event_id, student_id)
        SELECT e.event_id, %s
        FROM Events e
        WHERE e.event_id = %s
          AND e.type = %s
          AND e.status = %s
          AND e.event_date > CURRENT_TIMESTAMP
          AND EXISTS (
              SELECT 1 FROM Student s
              WHERE s.student_id = %s
          )
          AND NOT EXISTS (
              SELECT 1
              FROM Event_Participation ep
              WHERE ep.event_id = e.event_id
                AND ep.student_id = %s
          )
        """,
        (
            student_id,
            event_id,
            EVENT_PARTICIPATION,
            EVENT_SCHEDULED,
            student_id,
            student_id,
        )
    )

    if inserted == 1:
        return True, "Successfully registered for the event."

    return False, "Registration failed. Please refresh and check event availability."


def cancel_registration(event_id, student_id):
    """Cancel only the specified student's registration."""
    deleted = execute(
        """
        DELETE FROM Event_Participation
        WHERE event_id = %s AND student_id = %s
        """,
        (event_id, student_id)
    )

    if deleted == 1:
        return True, "Your registration has been cancelled."

    return False, "No registration found for this event."


def get_my_events(student_id):
    """Return all events registered by a particular student."""
    return fetch_all(
        """
        SELECT
            e.event_id,
            e.name,
            e.event_date,
            e.venue,
            e.type,
            e.status,
            c.club_name,
            ep.registered_at
        FROM Event_Participation ep
        JOIN Events e ON ep.event_id = e.event_id
        JOIN Club c ON e.club_id = c.club_id
        WHERE ep.student_id = %s
        ORDER BY e.event_date ASC
        """,
        (student_id,)
    )


def create_event(club_id, name, description, event_date, venue, event_type):
    """Create a new scheduled event for a club."""

    if event_type not in (EVENT_PARTICIPATION, EVENT_VIEW):
        return False, "Invalid event type."

    inserted = execute(
        """
        INSERT INTO Events
            (club_id, name, description, event_date, venue, type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            club_id,
            name,
            description,
            event_date,
            venue,
            event_type,
            EVENT_SCHEDULED,
        )
    )

    if inserted == 1:
        return True, "Event created successfully."

    return False, "Event could not be created."


def cancel_event(event_id, club_id):
    """Cancel an event only if it belongs to the given club."""

    event = fetch_one(
        """
        SELECT event_id, status
        FROM Events
        WHERE event_id = %s AND club_id = %s
        """,
        (event_id, club_id)
    )

    if event is None:
        return False, "Event not found in your club."

    if event["status"] == EVENT_CANCELLED:
        return False, "This event is already cancelled."

    updated = execute(
        """
        UPDATE Events
        SET status = %s
        WHERE event_id = %s
          AND club_id = %s
          AND status = %s
        """,
        (EVENT_CANCELLED, event_id, club_id, EVENT_SCHEDULED)
    )

    if updated == 1:
        return True, "Event cancelled successfully."

    return False, "Event could not be cancelled."


def get_event_participants(event_id):
    """Return students registered for a particular event."""
    return fetch_all(
        """
        SELECT
            s.student_id,
            s.name,
            s.email_id,
            s.department,
            ep.registered_at
        FROM Event_Participation ep
        JOIN Student s ON ep.student_id = s.student_id
        WHERE ep.event_id = %s
        ORDER BY s.name
        """,
        (event_id,)
    )


def get_club_stats():
    """Read club event statistics from the analytics view."""
    return fetch_all(
        """
        SELECT
            club_id,
            club_name,
            total_events,
            total_registrations
        FROM club_event_summary
        ORDER BY club_name
        """
    )
