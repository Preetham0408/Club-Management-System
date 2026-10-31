# Person B – Recruitment and Membership Module

## 1. Module Overview

The Recruitment and Membership module is developed by Person B for the Club Management System.

It lets club heads post recruitment drives, review applications and select or reject applicants. Students (and heads, who are also students) can see open drives and apply. Selecting an applicant adds them to the club as a Member. Club heads can also view their club's members and remove a Member.

### Main Features

- Display open recruitment drives with the club name, earliest deadline first.
- Apply to an open drive (business rules checked before inserting).
- View personal applications and their status.
- Post a recruitment drive as a Club Head.
- Review applications for each drive of the head's club.
- Select an applicant: status becomes Selected and a Member row is added, in one transaction.
- Reject a pending applicant.
- List the members of the head's club.
- Remove a Member (with a confirmation checkbox). The Head cannot be removed.

## 2. Files Developed

| File | Purpose |
|---|---|
| `database/Seed_recruitment.sql` | Inserts sample drives (two open, one closed) and applications. |
| `database/queries/recruitment_demo.sql` | Demonstrates the SQL concepts used by this module. |
| `app/queries/recruitment_queries.py` | Contains all recruitment and membership database operations. |
| `app/pages/2_Recruitment.py` | Recruitment user interface (student section and head section). |
| `app/pages/3_Members.py` | Member list and member removal (head only). |

## 3. Database Implementation

### Recruitment Table

Stores one row per recruitment drive.

- `rec_id`: Unique drive identifier.
- `club_id`: Club that posted the drive.
- `posted_on`: Date the drive was posted (defaults to today).
- `ends_on`: Last date to apply. A CHECK constraint requires `ends_on >= posted_on`.
- `description`: Description of the drive.

A drive is **open** while `ends_on >= CURRENT_DATE`.

### Applications Table

Stores one row per student application.

- `application_id`: Unique application identifier.
- `rec_id`: Drive applied to.
- `student_id`: Applicant.
- `applied_on`: Date of application (defaults to today).
- `status`: Pending, Selected or Rejected (CHECK constraint).

A UNIQUE constraint on `(rec_id, student_id)` means a student can apply to a drive only once. This is also why a rejected student cannot reapply.

### Club_Memberships Table (used by this module)

Selecting an applicant inserts a row with role `Member`. Removing a member deletes that row. Partial unique indexes guarantee one Head per club and one headship per student.

### Seed Data

| Drive | Ends on | Applications |
|---|---|---|
| Developer Club recruitment (open) | 2026-11-30 | CS25B1051 Pending, CS25B1047 Pending |
| Robotics Club recruitment (open) | 2026-11-30 | CS25B1047 Selected |
| Developer Club closed drive | 2026-09-30 | CS25B1051 Rejected, CS25B1002 Rejected |

All IDs are looked up by name with subqueries because the tables use SERIAL.

## 4. SQL Queries Demonstrated

All queries are saved in `database/queries/recruitment_demo.sql`.

| # | Query | Concepts |
|---|---|---|
| 1 | Open drives with club name, ordered by `ends_on` | JOIN, WHERE, ORDER BY |
| 2 | Drives with 2 or more applications | GROUP BY, HAVING, COUNT |
| 3 | Students who applied but are not members of that club | NOT EXISTS subquery |
| 4 | Set one application to Selected | UPDATE |
| 5 | Remove one member from a club | DELETE |
| 6 | Select an applicant and add them as a member | Transaction, UPDATE + INSERT, NOT EXISTS |

Queries 4 to 6 change data, so they run inside `BEGIN; ... ROLLBACK;` to keep the original data.

## 5. Python Backend Implementation

The file `app/queries/recruitment_queries.py` contains the following functions:

| Function | Purpose |
|---|---|
| `get_open_drives()` | Retrieves open drives with club names. |
| `create_drive(club_id, ends_on, description)` | Creates a drive for a club. |
| `get_drive_applications(rec_id)` | Retrieves the applications of one drive. |
| `apply_to_drive(rec_id, student_id)` | Checks the application rules, then inserts. Returns `(True, "Applied!")` or `(False, reason)`. |
| `select_application(application_id, club_id, student_id)` | Marks Selected and adds a Member in one transaction. |
| `reject_application(application_id)` | Marks a Pending application as Rejected. |
| `remove_member(club_id, student_id)` | Removes a Member. Refuses to remove a Head. |
| `get_club_drives(club_id)` | Helper: all drives (open and closed) of a club, with application counts. |
| `get_my_applications(student_id)` | Helper: applications made by one student. |

### Backend Validation

A student can apply only if:

- the drive exists and `ends_on` is today or later;
- the student has not applied to that drive before (a rejected student cannot reapply);
- the student is not already a member of that club;
- the student is not that club's head.

Other rules enforced:

- A drive cannot be created with an end date in the past.
- Only a Pending application can be selected or rejected.
- A head can select an application only if it belongs to a drive of their own club.
- The Head row can never be removed; only Member rows can be deleted.

### Transaction Used for Selecting an Applicant

Selecting an applicant changes two tables, so both steps run together:

```python
run_transaction([
    ("UPDATE Applications SET status = %s WHERE application_id = %s",
     (STATUS_SELECTED, application_id)),
    ("INSERT INTO Club_Memberships (club_id, student_id, role) "
     "SELECT %s, %s, %s WHERE NOT EXISTS ("
     "  SELECT 1 FROM Club_Memberships WHERE club_id = %s AND student_id = %s)",
     (club_id, student_id, ROLE_MEMBER, club_id, student_id)),
])
```

Both steps succeed or both are undone. Without a transaction, a failure after the UPDATE would leave an application marked Selected while the student is not a member. The `NOT EXISTS` check prevents inserting a duplicate membership.

All queries use `%s` placeholders, so values are sent separately from the SQL text. This prevents SQL injection.

## 6. Streamlit User Interface

### Recruitment Page – `2_Recruitment.py`

**Student and Club Head:**
- View open drives and apply.
- See whether they are already a member, already applied, or the head of that club.
- View their own applications and statuses.

**Club Head:**
- Post a new recruitment drive.
- View every drive of their club (open and closed) with its applications.
- Select or Reject Pending applications.

### Members Page – `3_Members.py`

**Club Head only:**
- View all members of their club (Head first).
- Remove a member by choosing them, ticking the confirmation checkbox and submitting.

## 7. Testing and Verification

Rebuild the database before testing so the seed data is fresh:

```
psql -U postgres -d club_management -v ON_ERROR_STOP=1 -f database/setup_all.sql
```

Test logins: Student `CS25B1002`, Club Head `CS25B1019` (Developer Club), Club Head `CS25B1002` (Robotics Club), Student `CS25B1047`.

To run a backend function directly, open a terminal in the `app` folder and run, for example:

```
python -c "from queries.recruitment_queries import apply_to_drive; print(apply_to_drive(1, 'CS25B1002'))"
```

In a freshly built database, `rec_id` 1 is the open Developer Club drive and `rec_id` 3 is the closed Developer Club drive. Confirm with `SELECT rec_id, description FROM Recruitment;`.

### Test 1 – Successful application

**Steps:**
1. Log in as Student `CS25B1002`.
2. Open the Recruitment page.
3. In the Developer Club drive, click **Apply**.

**Expected result:** A green "Applied!" message appears. The drive now shows "Your application is Pending" and the My Applications table lists it as Pending. `SELECT * FROM Applications WHERE student_id = 'CS25B1002';` shows a new Pending row.

**Actual result:** _(fill in after testing)_

### Test 2 – Applying twice shows an error

**Steps:**
1. Complete Test 1 so `CS25B1002` has already applied to drive 1.
2. In the `app` folder run `apply_to_drive(1, 'CS25B1002')` as shown above.

**Expected result:** `(False, 'You have already applied to this drive.')`. No second row is added to Applications. (The page hides the Apply button once a student has applied.)

**Actual result:** _(fill in after testing)_

### Test 3 – Applying after the deadline shows an error

**Steps:**
1. In the `app` folder run `apply_to_drive(3, 'CS25B1047')` (drive 3 is the closed drive).

**Expected result:** `(False, 'The deadline for this drive has passed.')`. No row is added to Applications. The closed drive is also missing from the Open Recruitment Drives list.

**Actual result:** _(fill in after testing)_

### Test 4 – Selecting a student adds them to Club_Memberships

**Steps:**
1. Log in as Club Head `CS25B1019`.
2. Open the Recruitment page and expand the open Developer Club drive.
3. Click **Select** next to Abhishek (`CS25B1051`).
4. Open the Members page.
5. In psql run `SELECT * FROM Club_Memberships WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club');`

**Expected result:** A green "Applicant selected and added as a club member." message appears. The application status is Selected. The Members page and the psql result show Abhishek with role Member next to the Head.

**Actual result:** _(fill in after testing)_

### Test 5 – Removing the head is refused

**Steps:**
1. Log in as Club Head `CS25B1002`.
2. Open the Members page.
3. Select Himasesha (`CS25B1002`) — Head, tick the confirmation checkbox and click **Remove Member**.

**Expected result:** A red "The club head cannot be removed." message appears. The member list is unchanged. (If the checkbox is not ticked, the page shows "Please tick the confirmation box first.")

**Actual result:** _(fill in after testing)_

## 8. Screenshots

Add screenshots of the following pages after capturing them:

1. Recruitment page as a Student, showing open drives and My Applications.
2. Recruitment page as a Club Head, showing the post-drive form and the applications with Select and Reject buttons.
3. Members page as a Club Head, showing the member list and the remove form.
4. The "club head cannot be removed" error message.

Save the screenshots inside `docs/sections/screenshots/` and add their image references here before final submission.

## 9. Important SQL Concepts Demonstrated

- `JOIN` to combine drives with club names.
- `WHERE` and `ORDER BY` to filter open drives and sort by deadline.
- `GROUP BY` with `COUNT()` to count applications per drive.
- `HAVING` to keep only drives with 2 or more applications.
- `NOT EXISTS` to find applicants who are not members of that club.
- `UPDATE` to set an application to Selected.
- `DELETE` to remove a member.
- Transactions (`BEGIN` / `ROLLBACK`, `run_transaction`) to change two tables safely.

## 10. Conclusion

The Recruitment and Membership module covers the full path from posting a drive to a student becoming a club member. It combines PostgreSQL queries, Python backend functions and Streamlit pages, and it enforces the application rules in both the Python checks and the database constraints.