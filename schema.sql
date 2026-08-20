CREATE DATABASE IF NOT EXISTS stock_alert_system;
USE stock_alert_system;

CREATE TABLE IF NOT EXISTS symbol (
    symbol_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stock_price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol_id INT,
    timestamp DATETIME,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    FOREIGN KEY (symbol_id) REFERENCES symbol(symbol_id),
    UNIQUE KEY unique_price (symbol_id, timestamp)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    role ENUM('Standard', 'Admin', 'Owner') DEFAULT 'Standard',
    failed_login_attempts INT DEFAULT 0,
    lock_until DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS userSymbol (
    user_id INT,
    symbol_id INT,
    PRIMARY KEY (user_id, symbol_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (symbol_id) REFERENCES symbol(symbol_id)
);
