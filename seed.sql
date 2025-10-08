-- Insert an HR user
INSERT INTO hr_users (name, email, password_hash) VALUES ('Alice HR', 'alice@example.com', 'hashed_pw_example');

-- Canonical skills
INSERT INTO skills (skill_name, canonical_name) VALUES
('python', 'Python'),
('sql', 'SQL'),
('postgresql', 'PostgreSQL'),
('docker', 'Docker'),
('data-structures', 'Data Structures');

-- Two sample candidates
INSERT INTO candidates (full_name, email, phone) VALUES
('Ravi Kumar', 'ravi.kumar@example.com', '+91-9876543210'),
('Sita Sharma', 'sita.sharma@example.com', '+91-9123456780');

-- Two sample resumes (raw_text small examples)
INSERT INTO resumes (candidate_id, filename, upload_path, raw_text, parsed_json, embedding) VALUES
(1, 'ravi_cv.docx', '/path/to/ravi_cv.docx', 'Ravi Kumar\nEmail: ravi.kumar@example.com\nSkills: Python, SQL, PostgreSQL\nExperience: 2 years', '{"parsed": {"name":"Ravi Kumar","email":"ravi.kumar@example.com","skills":["python","sql","postgresql"]}}', '[]'::jsonb),
(2, 'sita_cv.docx', '/path/to/sita_cv.docx', 'Sita Sharma\nEmail: sita.sharma@example.com\nSkills: Python, Data Structures\nExperience: Internship', '{"parsed": {"name":"Sita Sharma","email":"sita.sharma@example.com","skills":["python","data-structures"]}}', '[]'::jsonb);

-- Sample job
INSERT INTO jobs (hr_id, title, description, embedding) VALUES
(1, 'Junior DB Developer', 'Looking for a junior DB dev with SQL/Postgres and Python scripting.', '[]'::jsonb);

-- Link job skills
INSERT INTO job_skills (job_id, skill_id, required_level) VALUES
(1, (SELECT skill_id FROM skills WHERE skill_name='sql'), 2),
(1, (SELECT skill_id FROM skills WHERE skill_name='postgresql'), 2),
(1, (SELECT skill_id FROM skills WHERE skill_name='python'), 1);
