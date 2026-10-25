# 🎓 Campus Club & Event Management System

A robust, database-driven web application built for managing college student clubs, recruitment drives, event participation, and membership tracking. Developed as part of the Database Management Systems (DBMS) course project[cite: 14].

---

## 👥 Team Members
* **Team Size:** 3 Members
* **Tech Stack:** Python, Streamlit, PostgreSQL (`psycopg2`), Draw.io

---

## 🚀 Key Features & Functional Modules

1. **User & Role Management Module:**
   * Secure login routing based on roles: **Admin**, **Club Managers (Heads/Members)**, and **Students**.
   * Role-based constraints (e.g., a student can head at most one club but be a member of multiple)[cite: 12].

2. **Club Management Module (Admin):**
   * Create, rename, and delete clubs[cite: 12].
   * Assign or change single club heads with strict database integrity[cite: 12].

3. **Recruitment & Membership Module:**
   * Club heads can post recruitment drives, review applications, and manage student selections ('Pending', 'Selected', 'Rejected')[cite: 12].

4. **Event Management Module:**
   * Organize events (Participation or View type)[cite: 12], track student registrations, and manage venue details.

---

## 📂 Project Structure

```text
Club_Management_System/
│
├── assets/                  # ER diagrams and visual schemas
│   ├── ER_Diagram.png
│   └── Relational_Tables.png
│
├── database/                # SQL scripts
│   ├── Schema.sql           # DDL script (Tables, Constraints, Indexes)
│   └── Sample_data.sql      # DML script (Realistic test data)
│
├── docs/                    # Project instructions and report documents
│   └── DBS_Project_Instructions.pdf
│
├── app/                     # Application source code
│   └── main.py              # Main Streamlit UI entry point
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation