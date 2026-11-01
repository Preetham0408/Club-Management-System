-- Owner: B. Demo queries for the Recruitment and Membership module (viva + report)

-- 1. JOIN + WHERE + ORDER BY: open drives with the club name, earliest deadline first
SELECT r.rec_id, c.club_name, r.posted_on, r.ends_on, r.description
FROM Recruitment r
JOIN Club c ON c.club_id = r.club_id
WHERE r.ends_on >= CURRENT_DATE
ORDER BY r.ends_on;

-- 2. GROUP BY + HAVING: drives that have 2 or more applications
SELECT r.rec_id, r.description, COUNT(*) AS total_applications
FROM Recruitment r
JOIN Applications a ON a.rec_id = r.rec_id
GROUP BY r.rec_id, r.description
HAVING COUNT(*) >= 2;

-- 3. Subquery with NOT EXISTS: students who applied to a drive but are not members of that club
SELECT s.student_id, s.name, c.club_name, a.status
FROM Applications a
JOIN Recruitment r ON r.rec_id = a.rec_id
JOIN Club c ON c.club_id = r.club_id
JOIN Student s ON s.student_id = a.student_id
WHERE NOT EXISTS (
    SELECT 1 FROM Club_Memberships cm
    WHERE cm.club_id = r.club_id AND cm.student_id = a.student_id)
ORDER BY c.club_name, s.name;

-- 4. UPDATE: set one application to Selected (rolled back after the demo)
BEGIN;
UPDATE Applications SET status = 'Selected'
WHERE student_id = 'CS25B1051'
  AND rec_id = (SELECT rec_id FROM Recruitment WHERE description = 'Developer Club recruitment');
SELECT application_id, student_id, status FROM Applications;
ROLLBACK;

-- 5. DELETE: remove one member from a club (rolled back after the demo)
BEGIN;
DELETE FROM Club_Memberships
WHERE student_id = 'CS25B1051'
  AND club_id = (SELECT club_id FROM Club WHERE club_name = 'Robotics Club');
SELECT student_id, role FROM Club_Memberships
WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Robotics Club');
ROLLBACK;

-- 6. TRANSACTION: select an applicant = UPDATE + INSERT together (what select_application does)
BEGIN;
UPDATE Applications SET status = 'Selected'
WHERE student_id = 'CS25B1051'
  AND rec_id = (SELECT rec_id FROM Recruitment WHERE description = 'Developer Club recruitment');
INSERT INTO Club_Memberships (club_id, student_id, role)
SELECT club_id, 'CS25B1051', 'Member' FROM Club
WHERE club_name = 'Developer Club'
  AND NOT EXISTS (
    SELECT 1 FROM Club_Memberships cm
    WHERE cm.club_id = Club.club_id AND cm.student_id = 'CS25B1051');
SELECT cm.student_id, cm.role
FROM Club_Memberships cm
WHERE cm.club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club');
ROLLBACK;