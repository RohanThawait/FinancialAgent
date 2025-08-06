"""
Core application logic for the AI Finance Agent.

This module contains functions for:
1. Setting up the multi-tool LangChain agent.
2. Generating financial summaries.
3. Creating data visualizations.
"""

# --- Imports ---
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Load Environment Variables ---
load_dotenv()

# --- Constants ---
DB_PATH = "finance.db"
LLM_MODEL = "gemini-1.5-flash"

# --- Core Functions ---

def create_spending_pie_chart(username: str):
    """
    Queries the database for a user's spending data and generates a Plotly pie chart.

    Args:
        username: The username of the currently logged-in user.

    Returns:
        A Plotly Figure object if data is found, otherwise None.
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT Description, Amount FROM bank_transactions WHERE Type = 'Debit' AND username = '{username}'"
    
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    if df.empty:
        return None

    fig = px.pie(
        df, 
        names='Description', 
        values=df['Amount'].abs(), 
        title=f'Spending Breakdown for {username}',
        hole=.3
    )
    fig.update_traces(textinfo='percent+label')
    return fig

@st.cache_resource
def setup_agent(username: str, name: str):
    """
    Initializes and caches a multi-tool LangChain agent for a specific user.

    The agent is configured with two sets of tools:
    1. A SQL toolkit for querying the financial database.
    2. A custom tool for generating pie charts.

    Args:
        username: The unique username for database filtering.
        name: The user's full name for conversational context.

    Returns:
        An initialized LangChain AgentExecutor.
    """
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

    # 1. Define the custom pie chart tool
    pie_chart_tool = Tool(
        name="create_user_spending_pie_chart",
        func=lambda _: create_spending_pie_chart(username=username),
        description="""
        Use this tool ONLY when the user explicitly asks for a visual representation,
        pie chart, graph, or diagram of their spending. It is the ONLY way to generate a chart.
        The tool does not require any input. The output is a Plotly chart object.
        """,
    )

    # 2. Define the SQL toolkit
    sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = sql_toolkit.get_tools() + [pie_chart_tool]
    
    # 3. Define the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""
        You are a helpful financial assistant for a user named '{name}'.
        Their username for database queries is '{username}'.
        You have access to a set of tools to answer questions.
        IMPORTANT: All SQL queries MUST include a WHERE clause to filter by the user's username.
        Example: SELECT * FROM bank_transactions WHERE username = '{username}';
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 4. Create the agent and agent executor
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history", input_key="input", return_messages=True
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,  # Set to True for detailed debugging in the terminal
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    
    return agent_executor

def generate_financial_summary(agent, username: str):
    """
    Runs a series of pre-defined analytical questions through the agent
    to generate a formatted financial summary.

    Args:
        agent: The initialized LangChain agent.
        username: The username for the summary title.

    Returns:
        A formatted markdown string containing the financial summary.
    """
    questions = [
        "What was my total spending in the last 30 days?",
        "What were my top 3 spending categories in the last 30 days, by total amount spent in each category?",
        "What was my largest single transaction in the last 30 days?",
        "How many transactions did I make in the last 30 days?",
    ]
    
    summary = f"### Financial Summary for {username}\n\nHere is your financial briefing:\n"
    
    for q in questions:
        try:
            result = agent.invoke({"input": q})
            answer = result["output"]
            summary += f"\n**- {q}**\n  - {answer}"
        except Exception as e:
            summary += f"\n**- {q}**\n  - Error generating this insight: {e}"
            
    return summary