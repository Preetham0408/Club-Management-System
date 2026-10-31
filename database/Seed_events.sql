
-- Owner: C
-- Sample events for Developer Club and Robotics Club

-- ==========================================
-- 1. INSERT SAMPLE EVENTS
-- ==========================================

INSERT INTO Events
    (club_id, name, description, event_date, venue, type, status)
SELECT
    c.club_id,
    v.name,
    v.description,
    v.event_date,
    v.venue,
    v.type,
    v.status
FROM Club c
CROSS JOIN (
    VALUES
    (
        'Developer Club',
        'CodeSprint 2026',
        'Competitive programming challenge',
        TIMESTAMP '2026-11-10 09:00:00',
        'H05',
        'Participation',
        'Scheduled'
    ),
    (
        'Developer Club',
        'Tech Showcase',
        'Demonstration of student technology projects',
        TIMESTAMP '2026-11-15 10:00:00',
        'Auditorium',
        'View',
        'Scheduled'
    ),
    (
        'Developer Club',
        'AI Innovation Challenge',
        'Artificial intelligence project competition',
        TIMESTAMP '2026-11-22 09:00:00',
        'Lab 3',
        'Participation',
        'Scheduled'
    ),
    (
        'Robotics Club',
        'Robotics Exhibition',
        'Display of robotics projects',
        TIMESTAMP '2026-12-05 10:00:00',
        'Main Hall',
        'View',
        'Scheduled'
    ),
    (
        'Robotics Club',
        'Robot Battle Practice',
        'Robotics competition practice session',
        TIMESTAMP '2026-12-12 09:00:00',
        'Robotics Lab',
        'Participation',
        'Cancelled'
    )
) AS v(club_name, name, description, event_date, venue, type, status)
WHERE c.club_name = v.club_name
AND NOT EXISTS (
    SELECT 1
    FROM Events e
    WHERE e.club_id = c.club_id
      AND e.name = v.name
);

-- ==========================================
-- 2. INSERT EVENT REGISTRATIONS
-- ==========================================

INSERT INTO Event_Participation (event_id, student_id)
SELECT e.event_id, v.student_id
FROM (
    VALUES
        ('Developer Club', 'CodeSprint 2026', 'CS25B1051'),
        ('Developer Club', 'CodeSprint 2026', 'CS25B1047'),
        ('Developer Club', 'CodeSprint 2026', 'CS25B1019'),
        ('Developer Club', 'AI Innovation Challenge', 'CS25B1002'),
        ('Developer Club', 'AI Innovation Challenge', 'CS25B1051'),
        ('Developer Club', 'AI Innovation Challenge', 'CS25B1047')
) AS v(club_name, event_name, student_id)
JOIN Club c ON c.club_name = v.club_name
JOIN Events e
    ON e.club_id = c.club_id
   AND e.name = v.event_name
WHERE NOT EXISTS (
    SELECT 1
    FROM Event_Participation ep
    WHERE ep.event_id = e.event_id
      AND ep.student_id = v.student_id
);
