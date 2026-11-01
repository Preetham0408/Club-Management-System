-- Owner: A. Demo queries for the Admin / Club module (viva + report)

-- 1. SELECT with WHERE and ORDER BY
SELECT admin_id, name, office_number
FROM Admin
WHERE office_number LIKE 'OFF-%'
ORDER BY name;

-- 2. JOIN + LEFT JOIN: every club with its admin and head
SELECT c.club_name, a.name AS admin_name, s.name AS head_name
FROM Club c
JOIN Admin a ON a.admin_id = c.admin_id
LEFT JOIN Club_Memberships cm ON cm.club_id = c.club_id AND cm.role = 'Head'
LEFT JOIN Student s ON s.student_id = cm.student_id
ORDER BY c.club_name;

-- 3. GROUP BY + HAVING: clubs with at least 2 people
SELECT c.club_name, COUNT(*) AS total_members
FROM Club c
JOIN Club_Memberships cm ON cm.club_id = c.club_id
GROUP BY c.club_name
HAVING COUNT(*) >= 2;

-- 4. COUNT with GROUP BY: memberships per department
SELECT s.department, COUNT(*) AS memberships
FROM Club_Memberships cm
JOIN Student s ON s.student_id = cm.student_id
GROUP BY s.department
ORDER BY memberships DESC;

-- 5. MIN, MAX, AVG over a subquery in FROM: club size statistics
SELECT MIN(size) AS smallest_club, MAX(size) AS biggest_club, ROUND(AVG(size), 2) AS average_size
FROM (SELECT COUNT(*) AS size FROM Club_Memberships GROUP BY club_id) AS club_sizes;

-- 6. Subquery with NOT EXISTS: students who are not head of any club
SELECT s.student_id, s.name
FROM Student s
WHERE NOT EXISTS (
    SELECT 1 FROM Club_Memberships cm
    WHERE cm.student_id = s.student_id AND cm.role = 'Head');

-- 7. Scalar subqueries: dashboard counts
SELECT (SELECT COUNT(*) FROM Student) AS students,
       (SELECT COUNT(*) FROM Club)    AS clubs,
       (SELECT COUNT(*) FROM Recruitment WHERE ends_on >= CURRENT_DATE) AS open_drives;

-- 8. INSERT: create a club and its head in one transaction (rolled back after the demo)
BEGIN;
INSERT INTO Club (club_name, email, admin_id)
VALUES ('Music Club', 'music@iiitdm.ac.in',
        (SELECT admin_id FROM Admin WHERE email = 'robert.smith@college.edu'));
INSERT INTO Club_Memberships (club_id, student_id, role)
SELECT club_id, 'CS25B1047', 'Head' FROM Club WHERE club_name = 'Music Club';
SELECT c.club_name, cm.student_id, cm.role
FROM Club c JOIN Club_Memberships cm ON cm.club_id = c.club_id
WHERE c.club_name = 'Music Club';
ROLLBACK;

-- 9. UPDATE: rename a club
BEGIN;
UPDATE Club SET club_name = 'Developers Guild' WHERE club_name = 'Developer Club';
SELECT club_id, club_name FROM Club;
ROLLBACK;

-- 10. TRANSACTION: change the head of Developer Club (demote first, then promote)
BEGIN;
UPDATE Club_Memberships SET role = 'Member'
WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club') AND role = 'Head';
INSERT INTO Club_Memberships (club_id, student_id, role)
VALUES ((SELECT club_id FROM Club WHERE club_name = 'Developer Club'), 'CS25B1047', 'Head')
ON CONFLICT (student_id, club_id) DO UPDATE SET role = 'Head';
SELECT cm.student_id, cm.role
FROM Club_Memberships cm
WHERE cm.club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club');
ROLLBACK;

-- 11. CONSTRAINT TEST: a second head in the same club must FAIL (error is expected)
BEGIN;
INSERT INTO Club_Memberships (club_id, student_id, role)
VALUES ((SELECT club_id FROM Club WHERE club_name = 'Developer Club'), 'CS25B1047', 'Head');
-- ERROR: duplicate key value violates unique constraint "uk_club_one_head"
ROLLBACK;

-- 12. DELETE with ON DELETE CASCADE: deleting a club removes its related rows
BEGIN;
SELECT (SELECT COUNT(*) FROM Club_Memberships) AS memberships_before;
DELETE FROM Club WHERE club_name = 'Robotics Club';
SELECT (SELECT COUNT(*) FROM Club_Memberships) AS memberships_after;
ROLLBACK;

-- 13. FOREIGN KEY RESTRICT: deleting an admin who still manages clubs must FAIL
BEGIN;
DELETE FROM Admin WHERE admin_id = 1;
-- ERROR: violates foreign key constraint (ON DELETE RESTRICT)
ROLLBACK;