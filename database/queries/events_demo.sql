
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
