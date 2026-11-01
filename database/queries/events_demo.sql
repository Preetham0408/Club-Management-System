-- Owner: C
-- Events and Analytics SQL Demonstrations


-- ==========================================
-- 1. UPCOMING SCHEDULED EVENTS
-- Concepts: WHERE, ORDER BY
-- ==========================================

SELECT
    event_id,
    name,
    event_date,
    venue,
    type,
    status
FROM Events
WHERE status = 'Scheduled'
  AND event_date >= CURRENT_TIMESTAMP
ORDER BY event_date ASC;


-- ==========================================
-- 2. REGISTRATIONS PER EVENT
-- Concepts: LEFT JOIN, COUNT
-- ==========================================

SELECT
    e.event_id,
    e.name,
    COUNT(ep.participation_id) AS total_registrations
FROM Events e
LEFT JOIN Event_Participation ep
    ON e.event_id = ep.event_id
GROUP BY e.event_id, e.name
ORDER BY e.event_id;


-- ==========================================
-- 3. EVENT DATE AND REGISTRATION STATISTICS PER CLUB
-- Concepts: MIN, MAX, AVG, GROUP BY
-- ==========================================

SELECT
    c.club_name,
    MIN(e.event_date) AS earliest_event,
    MAX(e.event_date) AS latest_event,
    ROUND(AVG(e.registration_count), 2)
        AS average_registrations_per_event
FROM Club c
LEFT JOIN (
    SELECT
        e.event_id,
        e.club_id,
        e.event_date,
        COUNT(ep.participation_id) AS registration_count
    FROM Events e
    LEFT JOIN Event_Participation ep
        ON e.event_id = ep.event_id
    GROUP BY e.event_id, e.club_id, e.event_date
) e
    ON c.club_id = e.club_id
GROUP BY c.club_id, c.club_name
ORDER BY c.club_name;


-- ==========================================
-- 4. CLUBS WITH MORE THAN ONE EVENT
-- Concepts: GROUP BY, HAVING
-- ==========================================

SELECT
    c.club_name,
    COUNT(e.event_id) AS total_events
FROM Club c
JOIN Events e
    ON c.club_id = e.club_id
GROUP BY c.club_id, c.club_name
HAVING COUNT(e.event_id) > 1;


-- ==========================================
-- 5. STUDENTS WITH NO EVENT REGISTRATIONS
-- Concept: NOT EXISTS subquery
-- ==========================================

SELECT
    s.student_id,
    s.name
FROM Student s
WHERE NOT EXISTS (
    SELECT 1
    FROM Event_Participation ep
    WHERE ep.student_id = s.student_id
);


-- ==========================================
-- 6. CANCEL AN EVENT
-- Concept: UPDATE
-- Demonstration only: ROLLBACK preserves original data
-- ==========================================

BEGIN;

UPDATE Events
SET status = 'Cancelled'
WHERE name = 'CodeSprint 2026'
  AND club_id = (
      SELECT club_id
      FROM Club
      WHERE club_name = 'Developer Club'
  )
RETURNING event_id, name, status;

ROLLBACK;


-- ==========================================
-- 7. DELETE A REGISTRATION
-- Concept: DELETE
-- Demonstration only: ROLLBACK preserves original data
-- ==========================================

BEGIN;

DELETE FROM Event_Participation
WHERE event_id = (
    SELECT e.event_id
    FROM Events e
    JOIN Club c ON c.club_id = e.club_id
    WHERE e.name = 'CodeSprint 2026'
      AND c.club_name = 'Developer Club'
)
AND student_id = 'CS25B1051'
RETURNING participation_id, event_id, student_id;

ROLLBACK;


-- ==========================================
-- 8. READ CLUB EVENT SUMMARY
-- Concept: VIEW
-- ==========================================

SELECT *
FROM club_event_summary
ORDER BY club_name;

-- ==========================================
-- 9. EVENTS A STUDENT CAN REGISTER FOR
-- Concepts: JOIN, WHERE, NOT EXISTS subquery
-- Used by get_registrable_events(student_id) = the Register tab
-- ==========================================

SELECT
    e.event_id,
    c.club_name,
    e.name,
    e.event_date,
    e.venue
FROM Events e
JOIN Club c ON c.club_id = e.club_id
WHERE e.type = 'Participation'
  AND e.status = 'Scheduled'
  AND e.event_date > CURRENT_TIMESTAMP
  AND NOT EXISTS (
      SELECT 1
      FROM Event_Participation ep
      WHERE ep.event_id = e.event_id
        AND ep.student_id = 'CS25B1042'
  )
ORDER BY e.event_date;


-- ==========================================
-- 10. EVERY EVENT OF ONE CLUB WITH ITS REGISTRATION COUNT
-- Concepts: LEFT JOIN, COUNT, GROUP BY, subquery
-- Used by get_club_events(club_id) = the Manage events tab
-- Tech Showcase must show 0, not disappear
-- ==========================================

SELECT
    e.event_id,
    e.name,
    e.event_date,
    e.venue,
    e.type,
    e.status,
    COUNT(ep.participation_id) AS registrations
FROM Events e
LEFT JOIN Event_Participation ep
    ON ep.event_id = e.event_id
WHERE e.club_id = (
    SELECT club_id
    FROM Club
    WHERE club_name = 'Developer Club'
)
GROUP BY e.event_id, e.name, e.event_date, e.venue, e.type, e.status
ORDER BY e.event_date DESC;


-- ==========================================
-- 11. EVENTS ONE STUDENT REGISTERED FOR
-- Concepts: JOIN of three tables, WHERE, ORDER BY
-- Used by get_my_events(student_id) = the My events tab
-- ==========================================

SELECT
    e.event_id,
    e.name,
    c.club_name,
    e.event_date,
    e.venue,
    e.type,
    e.status,
    ep.registered_at,
    e.event_date > CURRENT_TIMESTAMP AS is_upcoming
FROM Event_Participation ep
JOIN Events e ON e.event_id = ep.event_id
JOIN Club c ON c.club_id = e.club_id
WHERE ep.student_id = 'CS25B1051'
ORDER BY e.event_date;


-- ==========================================
-- 12. STUDENTS REGISTERED FOR ONE EVENT
-- Concepts: JOIN, WHERE, ORDER BY
-- Used by get_event_participants(event_id)
-- ==========================================

SELECT
    s.student_id,
    s.name,
    s.email_id,
    s.department,
    ep.registered_at
FROM Event_Participation ep
JOIN Student s ON s.student_id = ep.student_id
WHERE ep.event_id = (
    SELECT e.event_id
    FROM Events e
    JOIN Club c ON c.club_id = e.club_id
    WHERE e.name = 'CodeSprint 2026'
      AND c.club_name = 'Developer Club'
)
ORDER BY s.name;