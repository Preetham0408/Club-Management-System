-- 1. Insert Admins
INSERT INTO Admin (name, email, office_number) VALUES
('Dr. Robert Smith', 'robert.smith@college.edu', 'OFF-101'),
('Prof. Linda Taylor', 'linda.taylor@college.edu', 'OFF-102');

-- 2. Insert Students
INSERT INTO Student (student_id, name, email_id, department) VALUES
('CS25B1019', 'Nandha Gopal', 'cs25b1019@iiitdm.ac.in', 'CSE'),
('CS25B1002', 'Himasesha', 'cs25b1002@iiitdm.ac.in', 'ECE'),
('CS25B1051', 'Abhishek', 'cs25b1051@iiitdm.ac.in', 'Mechanical'),
('CS25B1047', 'Mukesh', 'cs25b1047@iiitdm.ac.in', 'CSE');

-- 3. Insert Clubs
INSERT INTO Club (club_name, email, admin_id) VALUES
('Developer Club', 'developer@iiitdm.ac.in', 1),
('Robotics Club', 'robotics@iiitdm.ac.in', 2);

-- 4. Insert Club Memberships (Heads and Members)
INSERT INTO Club_Memberships (club_id, student_id, role) VALUES
(1, 'CS25B1019', 'Head'),
(2, 'CS25B1002', 'Head'),
(2, 'CS25B1019', 'Member'),
(2, 'CS25B1051', 'Member');

-- 5. Insert Events
INSERT INTO Events
    (club_id, name, description, event_date, venue, type)
VALUES
    (1, 'Hackathon 2026', '24-hour coding challenge','2026-12-24 09:00:00', 'H05', 'Participation'),
    (2, 'RoboWars', 'Robot battle competition','2026-12-25 14:00:00', 'Main Ground', 'Participation');

-- 6. Insert Event Participation
INSERT INTO Event_Participation
    (event_id, student_id, registered_at)
VALUES
    (1, 'CS25B1051', '2026-10-20 10:00:00'),
    (1, 'CS25B1002', '2026-10-21 11:30:00'),
    (2, 'CS25B1019', '2026-10-22 14:15:00');

SELECT setval(pg_get_serial_sequence('admin','admin_id'),        (SELECT MAX(admin_id) FROM Admin));
SELECT setval(pg_get_serial_sequence('club','club_id'),          (SELECT MAX(club_id) FROM Club));
SELECT setval(pg_get_serial_sequence('club_memberships','membership_id'), (SELECT MAX(membership_id) FROM Club_Memberships));
SELECT setval(pg_get_serial_sequence('events','event_id'),       (SELECT MAX(event_id) FROM Events));