# Part A: Problem, Design and Normalization

## 1. Problem statement
College clubs usually manage members, recruitment and events with paper forms,
chat groups and spreadsheets. Records are scattered, duplicated and easy to lose, and
nobody can see the whole picture. This project provides one database-backed application
where clubs are created and managed, students apply and join, and events are organized.

## 2. Objectives
- Store clubs, students, memberships, recruitment drives, applications and events in one PostgreSQL database.
- Enforce rules (one head per club, no duplicate applications, valid statuses) inside the database.
- Give each kind of user (Admin, Club Head, Student) only the features they need.
- Produce reports: members per club, events and registrations per club, pending applications.

## 3. Users
| User | Can do |
|---|---|
| Admin (faculty) | Create, rename and delete clubs; assign or change heads; view everything |
| Club Head (student) | Post recruitment drives, select or reject applicants, manage members, create and cancel events |
| Student | Apply to drives, register for events, view club statistics |

## 4. Functional modules
1. Login and roles  2. Club management (Admin)  3. Recruitment and membership  4. Events and analytics

## 5. Entities and relationships
| Relationship | Cardinality | Implemented by |
|---|---|---|
| Admin manages Club | 1 : N | Club.admin_id (FK) |
| Student is member of Club | M : N (with attribute role) | table Club_Memberships |
| Club posts Recruitment | 1 : N | Recruitment.club_id (FK) |
| Student applies to Recruitment | M : N (attributes applied_on, status) | table Applications |
| Club conducts Event | 1 : N | Events.club_id (FK) |
| Student registers for Event | M : N (attribute registered_at) | table Event_Participation |

## 6. Important constraints
| Constraint | Where | Purpose |
|---|---|---|
| PRIMARY KEY (SERIAL) | every table | unique row id |
| UNIQUE(club_name), UNIQUE(email) | Club | no duplicate clubs |
| UNIQUE(student_id, club_id) | Club_Memberships | a student joins a club only once |
| Unique partial index (club_id) WHERE role='Head' | Club_Memberships | at most one head per club |
| Unique partial index (student_id) WHERE role='Head' | Club_Memberships | a student heads at most one club |
| CHECK role IN ('Head','Member') | Club_Memberships | valid roles only |
| CHECK type IN ('Participation','View'), CHECK status IN ('Scheduled','Cancelled') | Events | valid values |
| CHECK status IN ('Pending','Selected','Rejected') | Applications | valid values |
| CHECK ends_on >= posted_on | Recruitment | valid dates |
| UNIQUE(rec_id, student_id) | Applications | one application per drive |
| UNIQUE(event_id, student_id) | Event_Participation | no double registration |
| ON DELETE CASCADE | memberships, events, drives, applications, registrations | removing a club or student cleans related rows |
| ON DELETE RESTRICT | Club.admin_id | an admin who manages clubs cannot be deleted |

## 7. Normalization
**1NF:** every column holds one atomic value; there are no repeating groups.
**2NF:** every table has a single-column key (SERIAL id or student_id). The tables that
combine two ids (Club_Memberships, Applications, Event_Participation) also have a surrogate
key, and their other columns (role, status, registered_at) depend on the whole pair.
**3NF / BCNF:** no non-key column depends on another non-key column.

| Table | Functional dependency | Result |
|---|---|---|
| Student | student_id → name, email_id, department | BCNF |
| Admin | admin_id → name, email, office_number | BCNF |
| Club | club_id → club_name, email, admin_id | BCNF |
| Club_Memberships | (club_id, student_id) → role | 3NF |
| Recruitment | rec_id → club_id, posted_on, ends_on, description | BCNF |
| Applications | (rec_id, student_id) → applied_on, status | 3NF |
| Events | event_id → club_id, name, description, event_date, venue, type, status | BCNF |
| Event_Participation | (event_id, student_id) → registered_at | 3NF |

**Design decision, avoiding redundancy:** the head is stored only as role = 'Head' in
Club_Memberships, not again as a column in Club. Storing it twice would allow the two
copies to disagree (an update anomaly). Likewise Applications stores rec_id, not club_id,
because the club can be found through Recruitment.