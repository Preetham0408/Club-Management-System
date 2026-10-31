# Person C – Events and Analytics Module

## 1. Module Overview

The Events and Analytics module is developed by Person C for the Club Management System.

It allows students and club heads to view and participate in events. Club heads can create, manage, and cancel events belonging to their own clubs. All authenticated users can view club statistics.

### Main Features

- Display upcoming events from all clubs.
- Register for Participation events.
- Cancel personal event registrations.
- View personally registered events.
- Create events as a Club Head.
- View participants registered for an event.
- Cancel events without deleting them.
- Display club-wise event and registration statistics.

## 2. Files Developed

| File | Purpose |
|---|---|
| `database/Seed_events.sql` | Inserts sample events and registrations. |
| `database/Views.sql` | Creates the `club_event_summary` view. |
| `database/queries/events_demo.sql` | Demonstrates event-related SQL queries. |
| `app/queries/event_queries.py` | Contains event-related database operations. |
| `app/pages/4_Events.py` | Provides the Events user interface. |
| `app/pages/5_Club_Stats.py` | Displays club statistics and charts. |

## 3. Database Implementation

### Events Table

The Events table stores event information.

Important attributes:

- `event_id`: Unique event identifier.
- `club_id`: Club organizing the event.
- `name`: Event name.
- `description`: Event description.
- `event_date`: Date and time of the event.
- `venue`: Event location.
- `type`: Participation or View.
- `status`: Scheduled or Cancelled.

### Event_Participation Table

Stores registrations made by students.

Important attributes:

- `participation_id`: Unique registration identifier.
- `event_id`: Registered event.
- `student_id`: Student who registered.
- `registered_at`: Registration timestamp.

A UNIQUE constraint on `(event_id, student_id)` prevents duplicate registrations.

## 4. SQL View – club_event_summary

The `club_event_summary` view displays the total number of events and registrations for each club.

```sql
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
```

### Purpose of the View

- `LEFT JOIN` ensures that clubs without events are also included.
- `COUNT(DISTINCT e.event_id)` counts each event only once.
- `COUNT(DISTINCT ep.participation_id)` counts registrations without duplication.
- `GROUP BY` produces one summary row per club.

## 5. Python Backend Implementation

The file `app/queries/event_queries.py` contains the following functions:

| Function | Purpose |
|---|---|
| `list_upcoming_events()` | Retrieves future events with club information. |
| `register_for_event(event_id, student_id)` | Registers a student for an eligible event. |
| `cancel_registration(event_id, student_id)` | Cancels a student's registration. |
| `get_my_events(student_id)` | Retrieves events registered by a student. |
| `create_event(club_id, name, description, event_date, venue, event_type)` | Creates an event for a club. |
| `cancel_event(event_id, club_id)` | Cancels an event belonging to the specified club. |
| `get_event_participants(event_id)` | Retrieves students registered for an event. |
| `get_club_stats()` | Retrieves club statistics from the SQL view. |

### Backend Validation

The backend enforces the following conditions:

- Only Participation events can be registered for.
- Events must have Scheduled status.
- Past events cannot be registered for.
- Duplicate registrations are prevented.
- Students must exist in the database.
- Event cancellation is restricted to the event's own club.
- Event cancellation updates the status instead of deleting the event.

## 6. Streamlit User Interface

### Events Page – `4_Events.py`

**Student:**
- View upcoming events.
- Register for eligible events.
- View personal registrations.
- Cancel personal registrations.

**Club Head:**
- Perform student event operations.
- Create events for their own club.
- View events belonging to their club.
- View event participants.
- Cancel their club's events.

**Administrator:**
- View events.
- Does not have permission to create or cancel events.

### Club Statistics Page – `5_Club_Stats.py`

The statistics page is available to Students, Club Heads, and Administrators.

It displays:

- Total number of clubs.
- Total number of events.
- Total number of registrations.
- Club-wise statistics in a table.
- Bar chart of event registrations by club.
- Bar chart of total events by club.

Statistics are read-only.

## 7. Testing and Verification

The following tests were performed during backend and UI development.

| Test | Expected result | Result |
|---|---|---|
| Register for a View event | Registration refused | Passed |
| Register for a Cancelled event | Registration refused | Passed |
| Duplicate registration | Registration refused | Passed |
| Register for a non-existent event | Registration refused | Passed |
| Register for an eligible Participation event | Registration succeeds | Passed |
| Cancel personal registration | Registration removed | Passed |
| Create an event as Club Head | Event created | Passed |
| Cancel an event as Club Head | Status changes to Cancelled | Passed |
| View participants | Correct participants displayed | Passed |
| Student Events page | Student operations available | Passed |
| Club Head Events page | Own-club management available | Passed |
| Administrator Events page | Read-only access | Passed |
| Club statistics | Values match SQL view | Passed |

### Database Verification

The verified database results during testing were:

| Club | Total Events | Total Registrations |
|---|---:|---:|
| Developer Club | 5 | 8 |
| Robotics Club | 3 | 1 |
| **Total** | **8** | **9** |

The event count includes a cancelled test event, which remains in the database by design.

## 8. Screenshots

Add screenshots of the following application pages after capturing them:

1. Events page as a Student.
2. Events page as a Club Head, showing event creation and management.
3. Events page as an Administrator.
4. Club Statistics page showing metrics, table, and charts.

Save the screenshots inside `docs/sections/screenshots/` and add their image references here before final submission.

## 9. Important SQL Concepts Demonstrated

- `WHERE` and `ORDER BY` for filtering and sorting.
- `LEFT JOIN` for retaining records without matching rows.
- `COUNT()` for counting registrations.
- `MIN()`, `MAX()`, and `AVG()` for aggregate calculations.
- `GROUP BY` for grouping club statistics.
- `HAVING` for filtering grouped results.
- `NOT EXISTS` for finding students without registrations.
- `UPDATE` for cancelling events.
- `DELETE` for cancelling registrations.
- `VIEW` for reusable club statistics.

## 10. Conclusion

The Events and Analytics module provides event management and club-wise analytics for the Club Management System.

It integrates PostgreSQL queries, Python backend functions, and Streamlit user interfaces while enforcing role-based permissions and event registration rules.
