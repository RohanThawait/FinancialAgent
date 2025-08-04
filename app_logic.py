# app_logic.py
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

# Load environment variables at the very top
load_dotenv()

@st.cache_resource
def setup_agent():
    print("Setting up agent for the first time...")
    DB_PATH = "finance.db"
    
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
        agent_type="openai-tools",
        verbose=False,
        agent_executor_kwargs={"memory": memory, "handle_parsing_errors": True},
    )
    return agent_executor