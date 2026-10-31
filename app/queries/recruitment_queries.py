# Owner: Person B. All SQL functions for the Recruitment and Membership module.
from datetime import date
import psycopg2
from database import fetch_all, fetch_one, execute, run_transaction
from constants import ROLE_HEAD, ROLE_MEMBER, STATUS_PENDING, STATUS_SELECTED, STATUS_REJECTED


def _db_error(e):
    """Turn a database error into a short message for the screen."""
    return False, "The database rejected this change: " + str(e).splitlines()[0]


# ---------- Read functions ----------

def get_open_drives():
    """Drives that are still open (JOIN + WHERE + ORDER BY)."""
    return fetch_all(
        "SELECT r.rec_id, r.club_id, c.club_name, r.posted_on, r.ends_on, r.description "
        "FROM Recruitment r JOIN Club c ON c.club_id = r.club_id "
        "WHERE r.ends_on >= CURRENT_DATE "
        "ORDER BY r.ends_on"
    )


def get_club_drives(club_id):
    """All drives (open and closed) of one club, newest deadline first."""
    return fetch_all(
        "SELECT rec_id, posted_on, ends_on, description FROM Recruitment "
        "WHERE club_id = %s ORDER BY ends_on DESC",
        (club_id,),
    )


def get_drive_applications(rec_id):
    """Applications of one drive. Ordering by status puts Pending first (P < R < S)."""
    return fetch_all(
        "SELECT a.application_id, s.student_id, s.name, s.department, a.applied_on, a.status "
        "FROM Applications a JOIN Student s ON s.student_id = a.student_id "
        "WHERE a.rec_id = %s ORDER BY a.status, s.name",
        (rec_id,),
    )


def get_my_applications(student_id):
    """Every application made by one student."""
    return fetch_all(
        "SELECT c.club_name, r.ends_on AS drive_ends_on, a.applied_on, a.status "
        "FROM Applications a "
        "JOIN Recruitment r ON r.rec_id = a.rec_id "
        "JOIN Club c ON c.club_id = r.club_id "
        "WHERE a.student_id = %s ORDER BY a.applied_on DESC",
        (student_id,),
    )


# ---------- Write functions (all return (True/False, message)) ----------

def create_drive(club_id, ends_on, description):
    description = (description or "").strip()
    if not description:
        return False, "Please write a short description."
    if ends_on < date.today():
        return False, "The last date cannot be in the past."
    try:
        execute("INSERT INTO Recruitment (club_id, ends_on, description) VALUES (%s, %s, %s)",
                (club_id, ends_on, description))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "Recruitment drive posted."


def apply_to_drive(rec_id, student_id):
    """Check the rules in Python, then insert. Returns (True, "Applied!") or (False, reason)."""
    drive = fetch_one(
        "SELECT club_id, ends_on >= CURRENT_DATE AS is_open FROM Recruitment WHERE rec_id = %s",
        (rec_id,),
    )
    if drive is None:
        return False, "Drive not found."
    if not drive["is_open"]:
        return False, "The deadline for this drive has passed."
    # A rejected student also has a row here, so they cannot reapply either.
    if fetch_one("SELECT 1 FROM Applications WHERE rec_id = %s AND student_id = %s",
                 (rec_id, student_id)):
        return False, "You have already applied to this drive."
    member = fetch_one("SELECT role FROM Club_Memberships WHERE club_id = %s AND student_id = %s",
                       (drive["club_id"], student_id))
    if member and member["role"] == ROLE_HEAD:
        return False, "You are the head of this club, so you cannot apply to it."
    if member:
        return False, "You are already a member of this club."
    try:
        # status is not given, so the table default 'Pending' is used
        execute("INSERT INTO Applications (rec_id, student_id) VALUES (%s, %s)",
                (rec_id, student_id))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "Applied!"


def select_application(application_id, club_id, student_id):
    """Mark the application Selected AND add the student as a Member, in ONE transaction:
    both steps succeed or both are undone."""
    application = fetch_one(
        "SELECT a.status FROM Applications a JOIN Recruitment r ON r.rec_id = a.rec_id "
        "WHERE a.application_id = %s AND r.club_id = %s AND a.student_id = %s",
        (application_id, club_id, student_id),
    )
    if application is None:
        return False, "Application not found in your club."
    if application["status"] != STATUS_PENDING:
        return False, "This application is already " + application["status"] + "."
    try:
        run_transaction([
            ("UPDATE Applications SET status = %s WHERE application_id = %s",
             (STATUS_SELECTED, application_id)),
            ("INSERT INTO Club_Memberships (club_id, student_id, role) "
             "SELECT %s, %s, %s WHERE NOT EXISTS ("
             "  SELECT 1 FROM Club_Memberships WHERE club_id = %s AND student_id = %s)",
             (club_id, student_id, ROLE_MEMBER, club_id, student_id)),
        ])
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "Applicant selected and added to the club."


def reject_application(application_id):
    """Only a Pending application can be rejected."""
    try:
        changed = execute(
            "UPDATE Applications SET status = %s WHERE application_id = %s AND status = %s",
            (STATUS_REJECTED, application_id, STATUS_PENDING),
        )
    except psycopg2.Error as e:
        return _db_error(e)
    if changed == 0:
        return False, "Only a pending application can be rejected."
    return True, "Application rejected."


def remove_member(club_id, student_id):
    """Remove a Member from a club. The Head can never be removed."""
    member = fetch_one("SELECT role FROM Club_Memberships WHERE club_id = %s AND student_id = %s",
                       (club_id, student_id))
    if member is None:
        return False, "This student is not a member of the club."
    if member["role"] == ROLE_HEAD:
        return False, "The club head cannot be removed."
    try:
        execute("DELETE FROM Club_Memberships WHERE club_id = %s AND student_id = %s",
                (club_id, student_id))
    except psycopg2.Error as e:
        return _db_error(e)
    return True, "Member removed."