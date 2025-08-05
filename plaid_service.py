# plaid_service.py
import os
import plaid
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from plaid.api import plaid_api
# We no longer need the Link Token imports, but we need new ones for the sandbox
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest

# --- Plaid Client Initialization (same as before) ---
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
DB_PATH = "finance.db"

host = plaid.Environment.Sandbox if PLAID_ENV == "sandbox" else plaid.Environment.Development
configuration = plaid.Configuration(
    host=host,
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET,}
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# --- NEW Sandbox Simulation Function ---
def create_sandbox_public_token():
    """
    Directly creates a public_token in the sandbox environment,
    bypassing the need for the Link UI popup.
    """
    try:
        # This special request is only available in the sandbox
        request = SandboxPublicTokenCreateRequest(
            institution_id='ins_109508', # A default sandbox institution
            initial_products=[Products('transactions')]
        )
        response = client.sandbox_public_token_create(request)
        return response['public_token']
    except plaid.ApiException as e:
        print(f"Plaid API error in create_sandbox_public_token: {e.body}")
        return None

# --- Other functions remain the same ---
def exchange_public_token(public_token: str):
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        return response['access_token'], response['item_id']
    except plaid.ApiException as e:
        print(f"Plaid API error in exchange_public_token: {e.body}")
        return None, None

def save_credentials_to_db(username, access_token, item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO plaid_items (username, access_token, item_id) VALUES (?, ?, ?)",
        (username, access_token, item_id)
    )
    conn.commit()
    conn.close()
    print(f"Saved credentials for user {username}, item {item_id}")

def get_transactions(access_token: str):
    try:
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )
        response = client.transactions_get(request)
        return response['transactions']
    except plaid.ApiException as e:
        print(f"Plaid API error in get_transactions: {e.body}")
        return []

def save_transactions_to_db(username: str, transactions: list):
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame(transactions)
    df_mapped = pd.DataFrame({
        'Date': pd.to_datetime(df['date']),
        'Description': df['name'],
        'Amount': -df['amount'],
        'Type': df['amount'].apply(lambda x: 'Debit' if x > 0 else 'Credit'),
        'username': username
    })
    df_mapped.to_sql('bank_transactions', conn, if_exists='append', index=False)
    conn.close()
    print(f"Saved {len(df_mapped)} new transactions for user {username}")