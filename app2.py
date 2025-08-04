# app.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from app_logic import setup_agent 

# --- Page Config ---
st.set_page_config(page_title="Finance Agent v3", page_icon="🔐", layout="centered")

# --- User Authentication ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
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

    agent = setup_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

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