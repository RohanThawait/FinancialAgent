"""
Main Streamlit web application for the AI Finance Agent.

This script handles:
1. User authentication and session management.
2. Rendering the user interface (sidebar, main chat, and feature sections).
3. Orchestrating calls to the backend logic in `app_logic.py` and `plaid_service.py`.
"""

# --- Imports ---
# Standard library imports
import os
import time
import yaml

# Third-party imports
import plotly.graph_objects as go
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

# Local application imports
from app_logic import setup_agent, generate_financial_summary
from plaid_service import (create_sandbox_public_token, exchange_public_token, 
                           save_credentials_to_db, get_transactions, 
                           save_transactions_to_db)

# --- UI Rendering Functions ---

def render_sidebar(authenticator, name: str):
    """Renders the sidebar with a welcome message and logout button."""
    st.sidebar.title(f"Welcome {name}")
    authenticator.logout('Logout', 'sidebar')

def render_plaid_section(username: str):
    """Renders the UI for Plaid integration to sync bank transactions."""
    with st.expander("🔗 Sync Bank Transactions"):
        st.write("Click to sync transactions from a sample bank account (Plaid Sandbox).")
        
        if st.button("Sync Sample Bank Transactions"):
            with st.spinner("Connecting to bank and syncing..."):
                public_token = create_sandbox_public_token()
                if not public_token:
                    st.error("Could not create public token. Check Plaid credentials.")
                    return

                access_token, item_id = exchange_public_token(public_token)
                if not access_token:
                    st.error("Failed to exchange public token.")
                    return

                save_credentials_to_db(username, access_token, item_id)
                st.write("Connection successful. Preparing transactions...")
                time.sleep(5)  # Wait for Plaid to prepare data

                transactions = get_transactions(access_token)
                if transactions:
                    save_transactions_to_db(username, transactions)
                    st.success(f"Successfully synced {len(transactions)} new transactions!")
                    st.balloons()
                else:
                    st.success("Connection successful, no new transactions found.")

def render_summary_section(agent, username: str):
    """Renders the UI for generating an on-demand financial summary."""
    if st.button("📊 Generate Financial Summary"):
        with st.spinner("🤖 Generating your financial summary..."):
            summary_report = generate_financial_summary(agent, username)
            st.session_state.messages.append({"role": "assistant", "content": summary_report})
            st.rerun()

def render_chat_interface(agent):
    """Renders the main chat history and input form."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], go.Figure):
                st.plotly_chart(message["content"])
            else:
                st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("Ask a question or for a chart..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Generate response if the last message is from the user
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    result = agent.invoke({"input": st.session_state.messages[-1]["content"]})
                    response = result["output"]
                    
                    # Check for chart objects in the agent's intermediate steps
                    if "intermediate_steps" in result and result["intermediate_steps"]:
                        tool_output = result["intermediate_steps"][-1][1]
                        if isinstance(tool_output, go.Figure):
                            response = tool_output
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

                except Exception as e:
                    error_message = f"Sorry, an error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    st.rerun()

# --- Main Application ---

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Finance Agent v3", page_icon="💡", layout="centered")

    # --- Authentication ---
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    authenticator = stauth.Authenticate(
        config['credentials'], config['cookie']['name'],
        config['cookie']['key'], config['cookie']['expiry_days']
    )
    
    authenticator.login('main')
    
    # --- Application Logic ---
    if st.session_state.get("authentication_status"):
        name = st.session_state["name"]
        username = st.session_state["username"]

        render_sidebar(authenticator, name)
        
        st.title("💡 AI Finance Agent v3")
        st.write("I can answer questions, create visualizations, and generate summaries!")

        agent = setup_agent(username=username, name=name)
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

        render_summary_section(agent, username)
        render_plaid_section(username)
        render_chat_interface(agent)

    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()