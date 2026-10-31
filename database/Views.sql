
-- Owner: C
-- Analytics view for club events and registrations

CREATE OR REPLACE VIEW club_event_summary AS

SELECT
    c.club_id,
    c.club_name,
    COUNT(DISTINCT e.event_id) AS total_events,
    COUNT(DISTINCT ep.participation_id) AS total_registrations

FROM Club c

LEFT JOIN Events e
    ON c.club_id = e.club_id

LEFT JOIN Event_Participation ep
    ON e.event_id = ep.event_id

GROUP BY
    c.club_id,
    c.club_name;
