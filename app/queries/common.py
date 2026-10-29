from database import fetch_all, fetch_one

def get_all_clubs():
    """Return all clubs as list of dicts."""
    return fetch_all("SELECT club_id, club_name FROM Club ORDER BY club_name")

def get_club_by_id(club_id):
    """Return one club or None."""
    return fetch_one("SELECT club_id, club_name, email, admin_id FROM Club WHERE club_id = %s", (club_id,))

def get_clubs_of_student(student_id):
    """Return all clubs this student is a member of."""
    return fetch_all(
        "SELECT c.club_id, c.club_name, cm.role "
        "FROM Club c JOIN Club_Memberships cm ON c.club_id = cm.club_id "
        "WHERE cm.student_id = %s ORDER BY c.club_name",
        (student_id,)
    )

def get_head_club(student_id):
    """Return the club this student heads, or None."""
    return fetch_one(
        "SELECT c.club_id, c.club_name FROM Club c "
        "JOIN Club_Memberships cm ON c.club_id = cm.club_id "
        "WHERE cm.student_id = %s AND cm.role = 'Head'",
        (student_id,)
    )

def get_club_members(club_id):
    """Return all members of a club, Head first, then Members."""
    return fetch_all(
        "SELECT s.student_id, s.name, cm.role "
        "FROM Student s JOIN Club_Memberships cm ON s.student_id = cm.student_id "
        "WHERE cm.club_id = %s ORDER BY cm.role ASC, s.name",
        (club_id,)
    )

def get_club_head(club_id):
    """Return the head student of a club, or None."""
    return fetch_one(
        "SELECT s.student_id, s.name "
        "FROM Student s JOIN Club_Memberships cm ON s.student_id = cm.student_id "
        "WHERE cm.club_id = %s AND cm.role = 'Head'",
        (club_id,)
    )

def student_exists(student_id):
    """Check if a student exists."""
    return fetch_one("SELECT 1 FROM Student WHERE student_id = %s", (student_id,)) is not None