"""
Database Setup Script for the AI Finance Agent.

This script initializes a new SQLite database (`finance.db`). It performs two main tasks:
1. Creates the necessary tables for the application.
2. Populates the tables with sample data from the `data/` directory for a default user.

To run, execute `python create_database.py` from the project's root directory.
This will delete and replace the existing `finance.db` file to ensure a clean setup.
"""

import sqlite3
import pandas as pd
import os

# --- Configuration Constants ---
DB_FILE = "finance.db"
DATA_DIR = "data"
CSV_FILES = {
    "bank_transactions": "bank_transactions.csv",
    "stock_portfolio": "stock_portfolio.csv",
    "mutual_funds": "mutual_funds.csv",
}
DEFAULT_USER = "jsmith"

def create_tables(conn):
    """
    Creates the database schema (tables).

    Args:
        conn: An active sqlite3 connection object.
    """
    cursor = conn.cursor()
    # Table for storing Plaid API credentials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plaid_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        access_token TEXT NOT NULL,
        item_id TEXT NOT NULL,
        UNIQUE(username, item_id)
    )
    """)
    # The data tables will be created by pandas later, but we ensure they don't exist
    # from a previous run to guarantee a clean slate.
    cursor.execute("DROP TABLE IF EXISTS bank_transactions")
    cursor.execute("DROP TABLE IF EXISTS stock_portfolio")
    cursor.execute("DROP TABLE IF EXISTS mutual_funds")
    conn.commit()
    print("Database schema created successfully.")

def populate_sample_data(conn, username):
    """
    Populates the database with sample data from CSV files for a given user.

    Args:
        conn: An active sqlite3 connection object.
        username: The default username to assign the sample data to.
    """
    print(f"\nAttempting to populate sample data for user: '{username}'...")
    try:
        for table_name, file_name in CSV_FILES.items():
            csv_path = os.path.join(DATA_DIR, file_name)
            df = pd.read_csv(csv_path)
            df['username'] = username
            # Use 'replace' to ensure that each run starts with fresh sample data
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"  - Table '{table_name}' populated with {len(df)} rows.")
        print("Sample data populated successfully.")
    except FileNotFoundError as e:
        print(f"Warning: Could not populate sample data. CSV file not found: {e.filename}")
    except Exception as e:
        print(f"An error occurred during data population: {e}")

def main():
    """
    Main function to orchestrate the database setup.
    """
    print(f"--- Initializing Database: {DB_FILE} ---")
    
    # Ensure a clean start by deleting the old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    try:
        # Use a 'with' statement for robust connection handling
        with sqlite3.connect(DB_FILE) as conn:
            create_tables(conn)
            populate_sample_data(conn, DEFAULT_USER)
        print(f"\n--- Database setup complete. ---")
    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()