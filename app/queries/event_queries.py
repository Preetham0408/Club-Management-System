# Owner: Person C. All SQL functions for the Events and Analytics module.
from datetime import datetime
import psycopg2
from database import fetch_all, fetch_one, execute
from constants import EVENT_PARTICIPATION, EVENT_VIEW, EVENT_SCHEDULED, EVENT_CANCELLED
from queries.common import student_exists


def _db_error(e):
    """Turn a database error into a short message for the screen."""
    return False, "The database rejected this change: " + str(e).splitlines()[0]


# ---------- Read functions ----------

def list_upcoming_events():
    """Future events of every club. Cancelled events are included so they can be shown
    (JOIN + WHERE + ORDER BY)."""
    return fetch_all(
        "SELECT e.event_id, e.club_id, c.club_name, e.name, e.description, "
        "       e.event_date, e.venue, e.type, e.status "
        "FROM Events e JOIN Club c ON c.club_id = e.club_id "
        "WHERE e.event_date >= CURRENT_TIMESTAMP "
        "ORDER BY e.event_date"
    )


def get_registrable_events(student_id):
    """Events this student can register for right now: Participation, Scheduled, in the
    future, and not registered yet (subquery with NOT EXISTS)."""
    return fetch_all(
        "SELECT e.event_id, c.club_name, e.name, e.event_date, e.venue "
        "FROM Events e JOIN Club c ON c.club_id = e.club_id "
        "WHERE e.type = %s AND e.status = %s AND e.event_date > CURRENT_TIMESTAMP "
        "  AND NOT EXISTS (SELECT 1 FROM Event_Participation ep "
        "                  WHERE ep.event_id = e.event_id AND ep.student_id = %s) "
        "ORDER BY e.event_date",
        (EVENT_PARTICIPATION, EVENT_SCHEDULED, student_id),
    )


def get_my_events(student_id):
    """Every event one student registered for. is_upcoming tells the page whether the
    event is still in the future (only those registrations can be cancelled)."""
    return fetch_all(
        "SELECT e.event_id, e.name, c.club_name, e.event_date, e.venue, e.type, e.status, "
        "       ep.registered_at, e.event_date > CURRENT_TIMESTAMP AS is_upcoming "
        "FROM Event_Participation ep "
        "JOIN Events e ON e.event_id = ep.event_id "
        "JOIN Club c ON c.club_id = e.club_id "
        "WHERE ep.student_id = %s ORDER BY e.event_date",
        (student_id,),
    )


def get_club_events(club_id):
    """All events of one club (past, future and cancelled) with the number of
    registrations. LEFT JOIN keeps events that have 0 registrations."""
    return fetch_all(
        "SELECT e.event_id, e.name, e.event_date, e.venue, e.type, e.status, "
        "       COUNT(ep.participation_id) AS registrations "
        "FROM Events e LEFT JOIN Event_Participation ep ON ep.event_id = e.event_id "
        "WHERE e.club_id = %s "
        "GROUP BY e.event_id, e.name, e.event_date, e.venue, e.type, e.status "
        "ORDER BY e.event_date DESC",
        (club_id,),
    )


def get_event_participants(event_id):
    """Students registered for one event."""
    return fetch_all(
        "SELECT s.student_id, s.name, s.email_id, s.department, ep.registered_at "
        "FROM Event_Participation ep JOIN Student s ON s.student_id = ep.student_id "
        "WHERE ep.event_id = %s ORDER BY s.name",
        (event_id,),
    )


def get_club_stats():
    """One row per club from the view club_event_summary (clubs with 0 events included)."""
    return fetch_all(
        "SELECT club_id, club_name, total_events, total_registrations "
        "FROM club_event_summary ORDER BY club_name"
    )


# ---------- Write functions (all return (True/False, message)) ----------

def register_for_event(event_id, student_id):
    """Check rule 7 in Python, then insert. Returns (True, msg) or (False, reason)."""
    event = fetch_one(
        "SELECT type, status, event_date > CURRENT_TIMESTAMP AS is_future "
        "FROM Events WHERE event_id = %s",
        (event_id,),
    )
    if event is None:
        return False, "Event not found."
    if event["type"] != EVENT_PARTICIPATION:
        return False, "You cannot register for a View event."
    if event["status"] != EVENT_SCHEDULED:
        return False, "This event is cancelled or not available."
    if not event["is_future"]:
        return False, "Registration is not allowed for past events."
    if not student_exists(student_id):
        return False, "Student not found."
    if fetch_one("SELECT 1 FROM Event_Participation WHERE event_id = %s AND student_id = %s",
                 (event_id, student_id)):
        return False, "You are already registered for this event."
    try:
        # registered_at is not given, so the table default (now) is used.
        # UNIQUE (event_id, student_id) is the safety net against a double click.
        execute("INSERT INTO Event_Participation (event_id, student_id) VALUES (%s, %s)",
                (event_id, student_id))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "You are registered for this event."


def cancel_registration(event_id, student_id):
    """Cancel one student's own registration: the row is deleted."""
    try:
        deleted = execute("DELETE FROM Event_Participation WHERE event_id = %s AND student_id = %s",
                          (event_id, student_id))
    except psycopg2.Error as e:
        return _db_error(e)
    if deleted == 0:
        return False, "You are not registered for this event."
    return True, "Your registration was cancelled."


def create_event(club_id, name, description, event_date, venue, event_type):
    """Create a Scheduled event for a club. event_date is a datetime."""
    name = (name or "").strip()
    description = (description or "").strip()
    venue = (venue or "").strip()
    if not name:
        return False, "Event name is required."
    if len(name) > 200:
        return False, "Event name can have at most 200 characters."
    if not venue:
        return False, "Venue is required."
    if len(venue) > 250:
        return False, "Venue can have at most 250 characters."
    if event_type not in (EVENT_PARTICIPATION, EVENT_VIEW):
        return False, "Invalid event type."
    if event_date <= datetime.now():
        return False, "Choose a future date and time."
    try:
        execute(
            "INSERT INTO Events (club_id, name, description, event_date, venue, type, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (club_id, name, description or None, event_date, venue, event_type, EVENT_SCHEDULED),
        )
    except psycopg2.Error as e:
        return _db_error(e)
    return True, f"Event '{name}' created."


def cancel_event(event_id, club_id):
    """Set status = 'Cancelled'. The row is never deleted. The event must belong to club_id,
    so a head can only cancel events of their own club."""
    event = fetch_one("SELECT status FROM Events WHERE event_id = %s AND club_id = %s",
                      (event_id, club_id))
    if event is None:
        return False, "Event not found in your club."
    if event["status"] == EVENT_CANCELLED:
        return False, "This event is already cancelled."
    try:
        changed = execute(
            "UPDATE Events SET status = %s WHERE event_id = %s AND club_id = %s AND status = %s",
            (EVENT_CANCELLED, event_id, club_id, EVENT_SCHEDULED),
        )
    except psycopg2.Error as e:
        return _db_error(e)
    if changed == 0:
        return False, "Event could not be cancelled."
    return True, "Event cancelled. It stays in the list, marked Cancelled."