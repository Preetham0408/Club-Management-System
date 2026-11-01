# Owner: Person A. All SQL functions for the Admin / Club module.
import psycopg2
from database import fetch_all, execute, run_transaction
from database import fetch_one
from constants import ROLE_HEAD, ROLE_MEMBER, EVENT_SCHEDULED, STATUS_PENDING
from queries.common import get_club_by_id, get_club_head, get_head_club, student_exists


def _db_error(e):
    """Turn a database error into a short message for the screen."""
    return False, "The database rejected this change: " + str(e).splitlines()[0]


# ---------- Read functions ----------

def get_system_overview():
    """One row of counts for the admin dashboard (scalar subqueries)."""
    return fetch_one(
        "SELECT (SELECT COUNT(*) FROM Student) AS students, "
        "       (SELECT COUNT(*) FROM Club) AS clubs, "
        "       (SELECT COUNT(*) FROM Recruitment WHERE ends_on >= CURRENT_DATE) AS open_drives, "
        "       (SELECT COUNT(*) FROM Events WHERE status = %s AND event_date > CURRENT_TIMESTAMP) AS upcoming_events, "
        "       (SELECT COUNT(*) FROM Applications WHERE status = %s) AS pending_applications",
        (EVENT_SCHEDULED, STATUS_PENDING),
    )


def get_clubs_overview():
    """Every club with its admin, head and member count (JOIN + LEFT JOIN + subquery)."""
    return fetch_all(
        "SELECT c.club_id, c.club_name, c.email AS club_email, "
        "       a.name AS admin_name, h.name AS head_name, "
        "       (SELECT COUNT(*) FROM Club_Memberships m WHERE m.club_id = c.club_id) AS total_members "
        "FROM Club c "
        "JOIN Admin a ON a.admin_id = c.admin_id "
        "LEFT JOIN Club_Memberships hm ON hm.club_id = c.club_id AND hm.role = %s "
        "LEFT JOIN Student h ON h.student_id = hm.student_id "
        "ORDER BY c.club_name",
        (ROLE_HEAD,),
    )


def get_all_admins():
    return fetch_all("SELECT admin_id, name FROM Admin ORDER BY name")


def get_students_available_as_head():
    """Students who do not head any club yet (subquery with NOT EXISTS)."""
    return fetch_all(
        "SELECT s.student_id, s.name FROM Student s "
        "WHERE NOT EXISTS ("
        "  SELECT 1 FROM Club_Memberships cm "
        "  WHERE cm.student_id = s.student_id AND cm.role = %s) "
        "ORDER BY s.name",
        (ROLE_HEAD,),
    )


def get_club_deletion_impact(club_id):
    """How many rows will disappear if this club is deleted (ON DELETE CASCADE)."""
    return fetch_one(
        "SELECT (SELECT COUNT(*) FROM Club_Memberships WHERE club_id = %s) AS memberships, "
        "       (SELECT COUNT(*) FROM Events WHERE club_id = %s) AS events, "
        "       (SELECT COUNT(*) FROM Recruitment WHERE club_id = %s) AS drives, "
        "       (SELECT COUNT(*) FROM Applications a JOIN Recruitment r ON r.rec_id = a.rec_id "
        "         WHERE r.club_id = %s) AS applications",
        (club_id, club_id, club_id, club_id),
    )


# ---------- Write functions (all return (True/False, message)) ----------

def create_club(name, email, admin_id, head_student_id):
    """Create a club AND its head in ONE transaction, so a club never exists without a head."""
    name, email = (name or "").strip(), (email or "").strip()
    if not name or not email:
        return False, "Club name and club email are required."
    if "@" not in email:
        return False, "Please enter a valid club email."
    if fetch_one("SELECT 1 FROM Club WHERE LOWER(club_name) = LOWER(%s)", (name,)):
        return False, "A club with this name already exists."
    if fetch_one("SELECT 1 FROM Club WHERE LOWER(email) = LOWER(%s)", (email,)):
        return False, "This club email is already used."
    if get_head_club(head_student_id):
        return False, "This student already heads another club."
    try:
        run_transaction([
            ("INSERT INTO Club (club_name, email, admin_id) VALUES (%s, %s, %s)",
             (name, email, admin_id)),
            # club_id is not known yet, so look it up by the (unique) name
            ("INSERT INTO Club_Memberships (club_id, student_id, role) "
             "SELECT club_id, %s, %s FROM Club WHERE club_name = %s",
             (head_student_id, ROLE_HEAD, name)),
        ])
    except psycopg2.Error as e:
        return _db_error(e)
    return True, f"Club '{name}' created."


def rename_club(club_id, new_name):
    new_name = (new_name or "").strip()
    if not new_name:
        return False, "The new name cannot be empty."
    if fetch_one("SELECT 1 FROM Club WHERE LOWER(club_name) = LOWER(%s) AND club_id <> %s",
                 (new_name, club_id)):
        return False, "Another club already uses this name."
    try:
        execute("UPDATE Club SET club_name = %s WHERE club_id = %s", (new_name, club_id))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, f"Club renamed to '{new_name}'."


def assign_head(club_id, new_head_id):
    """Change a club's head. The old head becomes a Member.
    ORDER MATTERS: demote first, then promote, because a club may have only one Head."""
    if not student_exists(new_head_id):
        return False, "Student not found."
    current = get_club_head(club_id)
    if current and current["student_id"] == new_head_id:
        return False, "This student is already the head of this club."
    other = get_head_club(new_head_id)
    if other:
        return False, f"This student already heads {other['club_name']}."
    try:
        run_transaction([
            ("UPDATE Club_Memberships SET role = %s WHERE club_id = %s AND role = %s",
             (ROLE_MEMBER, club_id, ROLE_HEAD)),
            # If the student is already a Member, promote that row; otherwise insert a new one.
            ("INSERT INTO Club_Memberships (club_id, student_id, role) VALUES (%s, %s, %s) "
             "ON CONFLICT (student_id, club_id) DO UPDATE SET role = EXCLUDED.role",
             (club_id, new_head_id, ROLE_HEAD)),
        ])
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "Club head changed."


def delete_club(club_id):
    """Deletes the club. Its memberships, events, registrations, drives and applications
    are removed automatically by ON DELETE CASCADE."""
    club = get_club_by_id(club_id)
    if club is None:
        return False, "Club not found."
    try:
        execute("DELETE FROM Club WHERE club_id = %s", (club_id,))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, f"Club '{club['club_name']}' and all its related data were deleted."