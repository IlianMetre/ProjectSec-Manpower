CREATE DATABASE ManpowerDB;

USE ManpowerDB;

CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50),
    prefix VARCHAR(10),
    lastname VARCHAR(50),
    email VARCHAR(100),
    password VARCHAR(100)
);

CREATE TABLE FS_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50),
    prefix VARCHAR(10),
    lastname VARCHAR(50),
    email VARCHAR(100),
    ip_addr VARCHAR(15)
);

INSERT INTO admin_users (firstname, prefix, lastname, email, password)
VALUES ('Jon', NULL, 'Doe', 'Jon.Doe@manpower.nl', '$2b$12$eX819XcEUZO.hEhY70ijb.OMdOxbkUUOyK9ijgYhoj5f059No7pyy');

