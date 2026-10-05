"""
Database helper for the Student Marketplace.
Uses MySQL for data storage.
"""

import os
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "student_marketplace"),
}


def get_db():
    """Return a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Create the database and items table if they do not exist."""
    config_no_db = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**config_no_db)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
    finally:
        cursor.close()
        conn.close()

    conn = get_db()
    cursor = conn.cursor()
    try:
        # sellers must be created first: items references it
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sellers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DOUBLE NOT NULL,
                category VARCHAR(100) NOT NULL,
                image_url TEXT,
                seller_name VARCHAR(255) NOT NULL,
                seller_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_sold TINYINT(1) DEFAULT 0,
                CONSTRAINT fk_items_seller
                    FOREIGN KEY (seller_id) REFERENCES sellers(id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            )
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
