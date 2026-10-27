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