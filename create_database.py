import sqlite3
import pandas as pd

def create_database():
    """
    Creates an SQLite database and populates it with data from CSV files.
    """
    # Read data from CSVs into pandas DataFrames
    try:
        transactions = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/bank_transaction.csv')
        stocks = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/stock_portfolio.csv')
        funds = pd.read_csv('C:/Users/Rohan/Projects/Project_8/FinancialAgent/data/mutual_funds.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure your CSV files are in the 'data' directory.")
        return

    # Connect to a new SQLite database
    conn = sqlite3.connect('finance.db')
    print("Database connection established.")

    # Use the DataFrames to create tables in the database
    transactions.to_sql('bank_transactions', conn, if_exists='replace', index=False)
    stocks.to_sql('stock_portfolio', conn, if_exists='replace', index=False)
    funds.to_sql('mutual_funds', conn, if_exists='replace', index=False)
    
    print("Tables 'bank_transactions', 'stock_portfolio', and 'mutual_funds' created successfully.")

    # Verify creation by printing table schemas
    cursor = conn.cursor()
    print("\n--- Database Schema ---")
    for table_name in ['bank_transactions', 'stock_portfolio', 'mutual_funds']:
        print(f"\nTable: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")

    # Close the connection
    conn.close()
    print("\nDatabase 'finance.db' created and populated successfully!")

if __name__ == '__main__':
    create_database()