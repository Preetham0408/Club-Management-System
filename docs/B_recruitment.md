# Part B: Recruitment and Membership Module

## Description
Club heads post recruitment drives, review the applications and Select or Reject each applicant.
Students (and heads, who are also students) see the open drives and apply. Selecting an applicant
adds them to the club as a Member. A club head can also see the members of the club and remove a Member.

Like the Admin page, the Recruitment page is built with tabs:
- Everyone: Open drives, Apply, My applications.
- Club head only: Post drive, Review applications.

The Members page (club head only) has two tabs: Member list and Remove member.

## How the application talks to the database
Pages never contain SQL. They call functions in app/queries/recruitment_queries.py (and
get_club_members from common.py). All values go through %s parameters, which prevents SQL injection.

| Function | What it does |
|---|---|
| get_open_drives() | Open drives with the club name (JOIN, WHERE, ORDER BY) |
| create_drive(club_id, ends_on, description) | Posts a drive |
| get_drive_applications(rec_id) | Applications of one drive |
| apply_to_drive(rec_id, student_id) | Checks the rules in Python, then inserts |
| select_application(application_id, club_id, student_id) | Selected + new Member row in one transaction |
| reject_application(application_id) | Pending -> Rejected |
| remove_member(club_id, student_id) | Deletes a Member; refuses to delete the Head |
| get_club_drives(club_id), get_my_applications(student_id) | Small helpers for the head and student tabs |

## Key design points
- A student can apply only if: the drive is not closed (ends_on is today or later), they have not
  applied to it before, they are not already a member of that club and not its head.
  A rejected student still has an Applications row, so they cannot reapply.
- Selecting an applicant changes two tables (Applications and Club_Memberships), so both steps run in
  ONE transaction (run_transaction). If one fails, both are undone. Without a transaction, a student
  could end up "Selected" but not a member. The NOT EXISTS in the INSERT stops a duplicate membership.
- Only a Pending application can be selected or rejected, and a head can only select applications
  of their own club.
- remove_member refuses to delete the Head. The Remove tab needs a confirmation checkbox.
- After every action the page reruns, and a message saved in session_state shows the result.

## SQL concepts demonstrated (database/queries/recruitment_demo.sql)
JOIN, WHERE, ORDER BY, GROUP BY, HAVING, COUNT, subquery with NOT EXISTS, UPDATE, DELETE, transaction
(BEGIN / ROLLBACK).

## Test cases
Rebuild the database first (setup_all.sql). In a fresh database rec_id 1 is the open Developer Club drive,
2 the open Robotics Club drive and 3 the closed Developer Club drive (check with `SELECT rec_id, description FROM Recruitment;`).

| # | What we test | Steps | Expected | Actual |
|---|---|---|---|---|
| 1 | Apply to an open drive | Log in as Student CS25B1042. Recruitment, Apply tab, choose Developer Club, Apply | "Applied!". My applications shows it as Pending | |
| 2 | Apply twice | Repeat test 1 with the same student and the same drive | "You have already applied to this drive." No new row in Applications | |
| 3 | Apply after the deadline | Open a terminal in the app folder and run `python -c "from queries.recruitment_queries import apply_to_drive; print(apply_to_drive(3, 'CS25B1042'))"` | `(False, 'The deadline for this drive has passed.')`. The closed drive is also missing from the Open drives tab | |
| 4 | Selecting a student adds a member | Log in as Club Head CS25B1019. Review applications tab, choose "Developer Club recruitment", pending applicant Rohith (CS25B1051), Select. Then open the Members page | "Applicant selected and added to the club." Rohith shows as Member, and his application is Selected | |
| 5 | Removing the head is refused | Log in as Club Head CS25B1002. Members page, Remove member tab, choose Himasesha (Head), tick the box, Remove | "The club head cannot be removed." The member list is unchanged | |
