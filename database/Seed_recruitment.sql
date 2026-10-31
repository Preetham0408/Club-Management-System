-- Insert Recruitment Drives
INSERT INTO Recruitment (club_id, ends_on, description)
VALUES
((SELECT club_id FROM Club WHERE club_name = 'Developer Club'), 
 '2026-11-30', 'Developer Club recruitment'),
((SELECT club_id FROM Club WHERE club_name = 'Robotics Club'), 
 '2026-11-30', 'Robotics Club recruitment');

-- Insert Applications
INSERT INTO Applications (rec_id, student_id, status)
VALUES
((SELECT rec_id FROM Recruitment WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club') LIMIT 1), 
 'CS25B1051', 'Pending'),
((SELECT rec_id FROM Recruitment WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Developer Club') LIMIT 1), 
 'CS25B1047', 'Pending'),
((SELECT rec_id FROM Recruitment WHERE club_id = (SELECT club_id FROM Club WHERE club_name = 'Robotics Club') LIMIT 1), 
 'CS25B1047', 'Selected');
-- Closed drive (for testing "apply after the deadline").
-- posted_on is given because the table checks ends_on >= posted_on.
INSERT INTO Recruitment (club_id, posted_on, ends_on, description)
VALUES
((SELECT club_id FROM Club WHERE club_name = 'Developer Club'),
 '2026-09-01', '2026-09-30', 'Developer Club closed drive');

-- Two old, already rejected applications on the closed drive
INSERT INTO Applications (rec_id, student_id, applied_on, status)
VALUES
((SELECT rec_id FROM Recruitment WHERE description = 'Developer Club closed drive'),
 'CS25B1051', '2026-09-15', 'Rejected'),
((SELECT rec_id FROM Recruitment WHERE description = 'Developer Club closed drive'),
 'CS25B1002', '2026-09-16', 'Rejected');