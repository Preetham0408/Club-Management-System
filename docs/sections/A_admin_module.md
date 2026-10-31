# Part A: Login and Admin Module

## Description
Users log in with their ID and a role (Student, Club Head, Admin). The role is stored in
the Streamlit session, and every page calls require_role() so only allowed roles can open it.
The Admin page has five tabs: Overview, Create club, Rename club, Change head, Delete club.

## How the application talks to the database
Pages never contain SQL. They call functions in app/queries/club_queries.py, which use
fetch_all / fetch_one / execute / run_transaction from database.py. All values go through %s
parameters, which prevents SQL injection.

## Key design points
- Creating a club inserts the club AND its head in one transaction, so a club never exists without a head.
- Changing a head is one transaction: the old head is demoted first, then the new head is promoted.
  The order matters because of the unique partial index (one head per club).
- Deleting a club shows how many rows will be removed and needs a confirmation checkbox.

## SQL concepts demonstrated (database/queries/admin_demo.sql)
JOIN, LEFT JOIN, GROUP BY, HAVING, COUNT, MIN, MAX, AVG, subqueries (NOT EXISTS, scalar, FROM),
INSERT, UPDATE, DELETE, transactions, ON CONFLICT, and constraint violation tests.

## Test cases
| # | What we test | Steps | Expected | Actual |
|---|---|---|---|---|
| 1 | Login: wrong admin id | Admin, enter "abc" | Error message, no crash | |
| 2 | Login: valid admin | Admin, enter 1 | Home page opens | |
| 3 | Create club | Create "Music Club" with head CS25B1047 | Club appears in Overview with that head | |
| 4 | Duplicate club name | Create "Music Club" again | "A club with this name already exists." | |
| 5 | Head of another club | Create a club with head CS25B1019 | "This student already heads another club." | |
| 6 | Change head | Make CS25B1051 head of Music Club | New head shown; old head is a Member | |
| 7 | Delete without confirmation | Press delete, box unticked | Error, club still exists | |
| 8 | Delete with confirmation | Tick box, delete | Club gone; its members, events and drives gone | |
| 9 | Role protection | Log in as Student and open the Admin page | "Your role cannot open this page." | |

(Add 2 screenshots: Overview tab and Change head tab.)