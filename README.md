# 🎓 Campus Club & Event Management System

A robust, database-driven web application built for managing college student clubs, recruitment drives, event participation, and membership tracking. Developed as part of the Database Management Systems (DBMS) course project.

---

## 👥 Team Members
* **Team Size:** 3 Members
* **Tech Stack:** Python, Streamlit, PostgreSQL (`psycopg2`), Draw.io

---

## 🚀 Key Features & Functional Modules

1. **User & Role Management Module:**
   * Secure login routing based on roles: **Admin**, **Club Managers (Heads/Members)**, and **Students**.
   * Role-based constraints (e.g., a student can head at most one club but be a member of multiple).

2. **Club Management Module (Admin):**
   * Create, rename, and delete clubs.
   * Assign or change single club heads with strict database integrity.

3. **Recruitment & Membership Module:**
   * Club heads can post recruitment drives, review applications, and manage student selections ('Pending', 'Selected', 'Rejected').

4. **Event Management Module:**
   * Organize events (Participation or View type), track student registrations, and manage venue details.

---

## 📂 Project Structure

```text
Club-Management-System/
├── app/
│   ├── main.py                  # A  login + home
│   ├── database.py              # A  connection + helpers (shared)
│   ├── auth.py                  # A  session + require_role()
│   ├── constants.py             # A  'Head','Member','Pending',...
│   ├── pages/                   # Streamlit auto-detects this folder
│   │   ├── 1_Admin_Clubs.py     # A
│   │   ├── 2_Recruitment.py     # B  (head view + student view)
│   │   ├── 3_Members.py         # B
│   │   ├── 4_Events.py          # C  (head/admin view + student view)
│   │   └── 5_Club_Stats.py      # C
│   └── queries/                 # SQL kept out of UI code
│       ├── common.py            # A  shared lookups
│       ├── club_queries.py      # A
│       ├── recruitment_queries.py  # B
│       └── event_queries.py     # C
├── database/
│   ├── Reset.sql                # A  drops all tables
│   ├── Schema.sql               # A  frozen after Day 2
│   ├── Sample_data.sql          # A  core data only
│   ├── Seed_recruitment.sql     # B
│   ├── Seed_events.sql          # C
│   ├── Views.sql                # C
│   └── queries/                 # demo queries for viva
│       ├── admin_demo.sql       # A
│       ├── recruitment_demo.sql # B
│       └── events_demo.sql      # C
├── docs/
│   ├── sections/                # A_*.md, B_*.md, C_*.md
│   ├── Report.docx              # A only, at the end
│   └── DBS_Project_Instructions.pdf
├── assets/                      # ER + relational diagrams (A)
├── .env.example  .gitignore  requirements.txt  README.md