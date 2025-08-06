import os
import sqlite3
import pytest

# Define the path to the database relative to the project root
DB_PATH = "finance.db"

def test_database_file_exists():
    """
    Tests if the database file 'finance.db' has been created in the root folder.
    """
    assert os.path.exists(DB_PATH), f"Database file not found at {DB_PATH}"

def test_database_tables_exist():
    """
    Tests if the database can be connected to and contains the expected tables.
    """
    # This test depends on the file existing, so we check again.
    if not os.path.exists(DB_PATH):
        pytest.fail("Database file not found, cannot test for tables.")

    expected_tables = {"bank_transactions", "stock_portfolio", "mutual_funds"}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query the database for a list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables_in_db = {row[0] for row in cursor.fetchall()}
        
        # Assert that the set of expected tables is a subset of what's in the DB
        assert expected_tables.issubset(tables_in_db), \
            f"Database is missing tables. Expected: {expected_tables}, Found: {tables_in_db}"

    except sqlite3.Error as e:
        pytest.fail(f"Database connection or query failed with error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()