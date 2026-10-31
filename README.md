# 🎓 Campus Club & Event Management System

A database-driven web application for managing college clubs, recruitment drives,
memberships and events. Built for the Database Management Systems (DBMS) course project.

## 👥 Team

| Member | Module |
|---|---|
| A: G Preetham Chowdary | Login & sessions, Admin / Club management, database design, integration |
| B: M Mukesh | Recruitment & Membership |
| C: P Abhishek Reddy | Events & Analytics |

**Tech stack:** Python, Streamlit, PostgreSQL (psycopg2), draw.io

## 🚀 Modules

1. **Login & roles:** Admin, Club Head and Student login by ID.
2. **Club management (Admin):** create, rename and delete clubs; assign or change a club's head.
3. **Recruitment & membership:** heads post drives and review applications; students apply; selection adds the student as a Member.
4. **Events & analytics:** heads create and cancel events; students register; statistics per club.

## 📂 Project structure

```text
Club-Management-System/
├── app/
│   ├── main.py                    # login + home            (A)
│   ├── database.py                # connection + helpers    (A)
│   ├── auth.py                    # session + require_role  (A)
│   ├── constants.py               # shared constants        (A)
│   ├── pages/
│   │   ├── 1_Admin_Clubs.py       # (A)
│   │   ├── 2_Recruitment.py       # (B)
│   │   ├── 3_Members.py           # (B)
│   │   ├── 4_Events.py            # (C)
│   │   └── 5_Club_Stats.py        # (C)
│   ├── queries/                   # all SQL used by the app
│   │   ├── common.py              # shared lookups          (A)
│   │   ├── club_queries.py        # (A)
│   │   ├── recruitment_queries.py # (B)
│   │   └── event_queries.py       # (C)
│   └── templates/page_template.py # starting point for a new page
├── database/
│   ├── Reset.sql  Schema.sql  Sample_data.sql  setup_all.sql   (A)
│   ├── Seed_recruitment.sql       # (B)
│   ├── Seed_events.sql  Views.sql # (C)
│   └── queries/                   # demo queries for viva: admin_demo.sql, recruitment_demo.sql, events_demo.sql
├── docs/                          # project instructions + report sections
├── assets/                        # ER diagram + relational schema
├── .env.example  .gitignore  requirements.txt  README.md
```

## ⚙️ How to run

1. Install Python 3.10+, PostgreSQL and Git.
2. Clone the repo and open it in a terminal.
3. Create the virtual environment and install packages:
   ```
   python -m venv venv
   venv\Scripts\activate          (Windows)   |   source venv/bin/activate   (Mac/Linux)
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and put your PostgreSQL password in `DB_PASSWORD`.
5. Build the database (run from the repo root):
   ```
   psql -U postgres -c "CREATE DATABASE club_management;"
   psql -U postgres -d club_management -v ON_ERROR_STOP=1 -f database/setup_all.sql
   ```
6. Start the app: `streamlit run app/main.py`

**Test logins:** Student `CS25B1019` · Club Head `CS25B1002` · Admin `1`

## 📜 Business rules

- A club head is also a student. One head per club, one club per head (enforced by the database).
- A member is a student with a `Club_Memberships` row.
- Selecting an application adds the student as a Member in the same transaction.
- Events are never deleted; cancelling sets `status = 'Cancelled'`.
- Deleting a club (Admin only) also deletes its memberships, events, drives and applications.
- Login uses only the ID, with no password. This is a deliberate simplification for the course project.