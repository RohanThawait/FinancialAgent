import sqlite3
import pandas as pd

def create_database_v3():
    """
    Creates a multi-user SQLite database with a table for Plaid credentials.
    """
    # --- Connect to DB and create cursor ---
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    print("Database connection established.")

    # --- Create plaid_items table ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plaid_items (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        access_token TEXT NOT NULL,
        item_id TEXT NOT NULL,
        UNIQUE(username, item_id)
    )
    """)
    print("Table 'plaid_items' is ready.")

    # --- Create sample data for 'jsmith' ---
    try:
        transactions = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/bank_transaction.csv')
        stocks = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/stock_portfolio.csv')
        funds = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/mutual_funds.csv')

        default_user = 'jsmith'
        transactions['username'] = default_user
        stocks['username'] = default_user
        funds['username'] = default_user

        transactions.to_sql('bank_transactions', conn, if_exists='replace', index=False)
        stocks.to_sql('stock_portfolio', conn, if_exists='replace', index=False)
        funds.to_sql('mutual_funds', conn, if_exists='replace', index=False)
        print(f"Sample data tables created/replaced for user '{default_user}'.")

    except FileNotFoundError as e:
        print(f"Sample data CSVs not found, skipping population. Error: {e}")

    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    create_database_v3()