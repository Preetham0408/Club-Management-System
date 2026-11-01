# Part C: Events and Analytics Module

## Description
Club heads create events for their own club and can cancel them. Students (and heads, who are also
students) see the upcoming events, register for Participation events, see the events they registered
for and cancel their own registration. Every logged-in user can open the Club statistics page, which
is read-only. The admin can view the events but cannot create or cancel them.

Like the Admin and Recruitment pages, the Events page is built with tabs:
- Everyone: Upcoming events.
- Student and club head: Register, My events.
- Club head only: Create event, Manage events (registered students and Cancel event).
- Admin: only the Upcoming events tab (view only).

The Club statistics page shows three totals (clubs, events, registrations), a table read from the view
`club_event_summary` and two bar charts (registrations per club, events per club).

## How the application talks to the database
Pages never contain SQL. They call functions in app/queries/event_queries.py, which use
fetch_all / fetch_one / execute from database.py. All values go through %s parameters, which prevents
SQL injection. Event types and statuses come from constants.py.

| Function | What it does |
|---|---|
| list_upcoming_events() | Future events of all clubs, cancelled ones included (JOIN, WHERE, ORDER BY) |
| get_registrable_events(student_id) | Events this student can register for right now (NOT EXISTS) |
| register_for_event(event_id, student_id) | Checks the rules in Python, then inserts. Returns (True, msg) or (False, reason) |
| cancel_registration(event_id, student_id) | Deletes the student's own registration row |
| get_my_events(student_id) | Events a student registered for (JOIN of three tables) |
| create_event(club_id, name, description, event_date, venue, event_type) | Checks the input, then inserts a Scheduled event |
| cancel_event(event_id, club_id) | Sets status to Cancelled after checking the event belongs to that club |
| get_club_events(club_id) | All events of one club with the number of registrations (LEFT JOIN, COUNT) |
| get_event_participants(event_id) | Students registered for one event |
| get_club_stats() | Reads the view club_event_summary |

## Key design points
- A student can register only if the event is of type Participation, has status Scheduled, has a future
  event_date, and the student is not registered yet. The checks run in Python so that each failure gives
  its own message. The table constraint UNIQUE (event_id, student_id) is the safety net behind them.
- An event is never deleted. Cancelling runs `UPDATE Events SET status = 'Cancelled'`. The event stays in
  the list marked Cancelled, its registrations and its history stay in the database, and the statistics
  stay correct. A DELETE would also remove all its registrations through ON DELETE CASCADE.
- cancel_event takes the head's club_id from the session and puts it in the WHERE clause, so a head can
  never cancel the event of another club. The page asks for a confirmation checkbox first, because there
  is no "un-cancel".
- Cancelling your own registration deletes that row. Only registrations for events that have not happened
  yet are offered for cancelling. Past events stay in the student's history.
- The Register list is filtered in SQL (NOT EXISTS), so a View event, a cancelled event, a past event or an
  event the student already joined never appears there.
- The view club_event_summary stores the club statistics query once. The page only runs a simple SELECT on
  it, and it always shows current data because a view is not a copy. LEFT JOIN is used so that a club with
  no events still appears with 0 (a plain JOIN would drop that club). COUNT(DISTINCT ...) is used because
  joining Events with Event_Participation repeats each event once per registration.

```sql
CREATE OR REPLACE VIEW club_event_summary AS
SELECT c.club_id, c.club_name,
       COUNT(DISTINCT e.event_id) AS total_events,
       COUNT(DISTINCT ep.participation_id) AS total_registrations
FROM Club c
LEFT JOIN Events e ON c.club_id = e.club_id
LEFT JOIN Event_Participation ep ON e.event_id = ep.event_id
GROUP BY c.club_id, c.club_name;
```

- After every action the page reruns, and a message saved in session_state shows the result.
- The admin has no registrations (the admin is not a student), so the page does not load them for the admin.

## SQL concepts demonstrated (database/queries/events_demo.sql)
WHERE and ORDER BY, LEFT JOIN, COUNT, MIN / MAX / AVG, GROUP BY with HAVING, subquery with NOT EXISTS,
scalar subquery, JOIN of three tables, UPDATE (cancel an event), DELETE (cancel a registration),
VIEW, transaction (BEGIN / ROLLBACK) for the demo of UPDATE and DELETE.

## Test cases
Rebuild the database first (setup_all.sql) and run the tests in this order. Run the `python -c` commands
in a terminal opened in the app folder. Test logins: Student CS25B1042, Club Head CS25B1019 (Developer Club).

| # | What we test | Steps | Expected | Actual |
|---|---|---|---|---|
| 1 | Registering for a View event is refused | Run `python -c "from database import fetch_one; from queries.event_queries import register_for_event; e = fetch_one('SELECT event_id FROM Events WHERE name = %s', ('Tech Showcase',)); print(register_for_event(e['event_id'], 'CS25B1042'))"`. Also open Events, Register tab, and look for Tech Showcase | `(False, 'You cannot register for a View event.')`. Tech Showcase is missing from the Register list | |
| 2 | Registering for a past event is refused | In psql: `INSERT INTO Events (club_id, name, description, event_date, venue, type) VALUES ((SELECT club_id FROM Club WHERE club_name = 'Developer Club'), 'Past Test Event', 'test', '2026-10-01 10:00:00', 'H05', 'Participation');`. Then run the command of test 1 with 'Past Test Event'. Finally delete it: `DELETE FROM Events WHERE name = 'Past Test Event';` | `(False, 'Registration is not allowed for past events.')`. No new row in Event_Participation | |
| 3 | Registering twice is refused | Log in as Student CS25B1042. Events, Register tab, choose CodeSprint 2026, Register. Then run the command of test 1 with 'CodeSprint 2026'. Then run `SELECT COUNT(*) FROM Event_Participation WHERE student_id = 'CS25B1042';` | First: "You are registered for this event." and the event appears in My events and leaves the Register list. Second: `(False, 'You are already registered for this event.')`. Count is 1 | |
| 4 | A cancelled event cannot be registered for | Log in as Student CS25B1042. Open the Upcoming events tab and find Robot Battle Practice. Open the Register tab. Then run the command of test 1 with 'Robot Battle Practice' | Robot Battle Practice is listed with status Cancelled but is missing from the Register list. `(False, 'This event is cancelled or not available.')` | |
| 5 | The statistics page matches the SQL output | Open Club statistics (any role). In psql run `SELECT * FROM club_event_summary ORDER BY club_name;` | Table and SQL result show the same numbers. After tests 1-4: Developer Club 4 events and 9 registrations, Robotics Club 3 events and 1 registration. The totals in the metrics are 7 events and 10 registrations | |
| 6 | A head cancels an event and the row is kept | Log in as Club Head CS25B1019. Create event tab: "Test Meetup", venue H05, a date 10 days ahead, type Participation. Manage events tab: choose Test Meetup, press Cancel event without ticking the box, then tick the box and press it again. Run `SELECT name, status FROM Events WHERE name = 'Test Meetup';` | "Event 'Test Meetup' created." Without the tick: "Tick the confirmation box first." After the tick: "Event cancelled. It stays in the list, marked Cancelled." The SELECT returns the row with status Cancelled (not deleted). Test Meetup is missing from the Register list | |

(Add 3 screenshots: Register tab as a student, Manage events tab as a club head, Club statistics page.
Save them in docs/sections/screenshots/ and add the image links here.)