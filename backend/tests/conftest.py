"""
Pytest fixtures for the Student Marketplace backend tests.
"""

import os
import sys
import pytest
import mysql.connector
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TEST_DB_NAME = "test_student_marketplace"


@pytest.fixture(autouse=True)
def test_database():
    """Use a fresh MySQL test database for every test."""
    import database

    # Create the test database
    config_no_db = {k: v for k, v in database.DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**config_no_db)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cursor.close()
    conn.close()

    # Point the app at the test database
    database.DB_CONFIG["database"] = TEST_DB_NAME
    database.init_db()

    # Seed a few items for read-oriented tests
    db = database.get_db()
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO items (title, description, price, category, seller_name, is_sold)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        ('Test Book', 'A test book', 12.50, 'Books', 'Alice', 0),
    )
    cur.execute(
        """
        INSERT INTO items (title, description, price, category, seller_name, is_sold)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        ('Test Laptop', 'A test laptop', 350.00, 'Electronics', 'Bob', 0),
    )
    cur.execute(
        """
        INSERT INTO items (title, description, price, category, seller_name, is_sold)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        ('Sold Chair', 'Already sold', 80.00, 'Furniture', 'Chloe', 1),
    )
    db.commit()
    cur.close()
    db.close()

    yield TEST_DB_NAME

    # Cleanup
    conn = mysql.connector.connect(**config_no_db)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cursor.close()
    conn.close()


@pytest.fixture()
def client():
    """Return a FastAPI TestClient."""
    from app import app
    return TestClient(app)
