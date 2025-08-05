# app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
# Updated imports for the new flow
from app_logic import setup_agent
from plaid_service import create_sandbox_public_token, exchange_public_token, save_credentials_to_db, get_transactions, save_transactions_to_db

# --- Page Config & Auth (same as before) ---
st.set_page_config(page_title="Finance Agent v3", page_icon="🔐", layout="centered")
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    config['credentials'], config['cookie']['name'],
    config['cookie']['key'], config['cookie']['expiry_days']
)
authenticator.login('main')
name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# --- Main Application Logic ---
if authentication_status:
    # --- Sidebar ---
    st.sidebar.title(f"Welcome {name}")
    authenticator.logout('Logout', 'sidebar')

    # --- Main Chat UI ---
    st.title("💰 AI Finance Agent")
    st.write("Your personal financial assistant. Ask away!")

    # --- Plaid Integration UI (Simplified) ---
    with st.expander("🔗 Sync Bank Transactions"):
        st.write("Click the button to sync transactions from a sample bank account (via Plaid Sandbox).")
        
        if st.button("Sync Sample Bank Transactions"):
            with st.spinner("Connecting to bank and syncing transactions..."):
                # 1. Simulate the link to get a public token
                public_token = create_sandbox_public_token()
                
                if public_token:
                    # 2. Exchange token and fetch/save data (same as before)
                    access_token, item_id = exchange_public_token(public_token)
                    if access_token:
                        save_credentials_to_db(username, access_token, item_id)
                        transactions = get_transactions(access_token)
                        if transactions:
                            save_transactions_to_db(username, transactions)
                            st.success(f"Successfully synced {len(transactions)} new transactions!")
                            st.balloons()
                        else:
                            st.success("Connection successful, but no new transactions found.")
                    else:
                        st.error("Failed to exchange public token. Please try again.")
                else:
                    st.error("Could not create a sandbox public token. Check Plaid credentials.")

    # --- Agent and Chat (same as before) ---
    agent = setup_agent(username=username, name=name)
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]
    # ... (rest of the chat logic is identical)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your finances..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    result = agent.invoke({"input": prompt})
                    response = result["output"]
                    st.markdown(response)
                except Exception as e:
                    response = f"Sorry, an error occurred: {e}"
                    st.error(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')