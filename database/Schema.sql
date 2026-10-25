CREATE TABLE IF NOT EXISTS Student(
	student_id VARCHAR(20) PRIMARY KEY,
	name VARCHAR(150) NOT NULL,
	email_id VARCHAR(100) UNIQUE NOT NULL,
	department VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Admin(
	admin_id INT PRIMARY KEY,
	name VARCHAR(150) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	office_number VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Club(
	club_id INT PRIMARY KEY,
	club_name VARCHAR(150) UNIQUE NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	admin_id INT NOT NULL,
	FOREIGN KEY (admin_id) REFERENCES Admin(admin_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Club_Memberships(
	membership_id INT PRIMARY KEY,
	club_id INT NOT NULL,
	student_id VARCHAR(20) NOT NULL,
	role VARCHAR(100) NOT NULL CHECK (role IN('Head','Member')),
	FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
	FOREIGN KEY (club_id) REFERENCES Club(club_id) ON DELETE CASCADE,
	CONSTRAINT unique_student_club UNIQUE (student_id,club_id)
);
CREATE UNIQUE INDEX uk_club_one_head 
ON Club_Memberships(club_id) 
WHERE role = 'Head';

CREATE UNIQUE INDEX uk_student_one_head
ON Club_Memberships(student_id) 
WHERE role = 'Head';

CREATE TABLE IF NOT EXISTS Events(
	event_id INT PRIMARY KEY,
	club_id INT NOT NULL,
	name VARCHAR(200) NOT NULL,
	description TEXT,
	event_date TIMESTAMP NOT NULL,
	venue VARCHAR(250) NOT NULL,
	type VARCHAR(50) NOT NULL CHECK(type IN('Participation','View')),
	FOREIGN KEY (club_id) REFERENCES Club(club_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Event_Participation(
	participation_id SERIAL PRIMARY KEY,
	event_id INT NOT NULL,
	student_id VARCHAR(20) NOT NULL,
	registered_at TIMESTAMP NOT NULL,
	FOREIGN KEY(event_id) REFERENCES Events(event_id) ON DELETE CASCADE,
	FOREIGN KEY(student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
	CONSTRAINT unique_event_student UNIQUE (event_id,student_id)
);

CREATE TABLE IF NOT EXISTS Recruitment(
	rec_id SERIAL PRIMARY KEY,
	club_id INT NOT NULL,
	posted_on DATE NOT NULL,
	ends_on DATE NOT NULL,
	description TEXT,
	FOREIGN KEY(club_id) REFERENCES Club(club_id) ON DELETE CASCADE,
	CONSTRAINT check_dates CHECK (ends_on >= posted_on)
);

CREATE TABLE IF NOT EXISTS Applications(
	application_id INT PRIMARY KEY,
	rec_id INT NOT NULL,
	student_id VARCHAR(20) NOT NULL,
	applied_on DATE NOT NULL,
	status VARCHAR(10) NOT NULL CHECK(status IN('Pending','Selected','Rejected')),
	FOREIGN KEY (rec_id) REFERENCES Recruitment(rec_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
	CONSTRAINT unique_rec_student UNIQUE (rec_id,student_id)
);