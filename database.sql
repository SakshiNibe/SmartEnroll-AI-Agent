CREATE DATABASE smartenroll_ai;

USE smartenroll_ai;

CREATE TABLE students(
    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100),
    dob VARCHAR(20),
    gender VARCHAR(20),
    aadhaar VARCHAR(20),

    board VARCHAR(100),
    seat_no VARCHAR(50),
    passing_year VARCHAR(20),
    percentage VARCHAR(20)
);