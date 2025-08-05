# app_logic.py
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

load_dotenv()

# The agent setup now takes the username as an argument
# This means a new agent will be cached for each user
# The agent setup now takes both username and the full name
@st.cache_resource
def setup_agent(username: str, name: str):
    print(f"Setting up agent for user: {username} ({name})...")
    DB_PATH = "finance.db"
    
    # Update the suffix to include the user's full name
    agent_suffix = f"""
IMPORTANT: You MUST filter all your queries by the current user's username.
The current user's username is '{username}' and their full name is '{name}'.
For example: 'SELECT * FROM bank_transactions WHERE username = '{username}';'
"""
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    memory = ConversationBufferMemory(
        memory_key="chat_history", input_key="input", return_messages=True
    )
    chat_history_placeholder = MessagesPlaceholder(variable_name="chat_history")
    
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        extra_prompt_messages=[chat_history_placeholder],
        suffix=agent_suffix,
        agent_type="openai-tools",
        verbose=False,
        agent_executor_kwargs={"memory": memory, "handle_parsing_errors": True},
    )
    return agent_executor