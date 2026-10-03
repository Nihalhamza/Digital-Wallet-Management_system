CREATE DATABASE digital_wallet_db;
USE digital_wallet_db;

CREATE TABLE users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    created_date DATE
);

CREATE TABLE wallet(
    wallet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    balance DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY(user_id)REFERENCES users(user_id)
);

CREATE TABLE transactions(
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    amount DECIMAL(10,2),
    transaction_date DATE,
    status VARCHAR(20),
    FOREIGN KEY(sender_id)REFERENCES users(user_id),
    FOREIGN KEY(receiver_id)REFERENCES users(user_id)
);

CREATE TABLE admin(
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(100)
);

SHOW TABLES;

SELECT * FROM users;
SELECT * FROM wallet;
