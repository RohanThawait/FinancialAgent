import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder

# --- Page Config ---
st.set_page_config(page_title="Finance Agent v2", page_icon="💰", layout="centered")

# --- Component Initialization ---
load_dotenv()
DB_PATH = "finance.db"

@st.cache_resource
def setup_agent():
    """
    Sets up and caches the LangChain agent and its components.
    This function runs only once.
    """
    print("Setting up agent for the first time...")
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
        # Set verbose to False here for a clean UI
        verbose=False,
        agent_executor_kwargs={"memory": memory, "handle_parsing_errors": True},
    )
    return agent_executor

def main():
    """
    The main function that defines the Streamlit UI.
    """
    st.title("💰 AI Finance Agent v2")
    st.write("Ask complex questions about your financial data, and the agent will write SQL to find the answer.")

    # Get the cached agent
    agent = setup_agent()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you with your finances today?"}]

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("E.g., Which stock has the highest profit?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking and writing SQL..."):
                try:
                    # The incorrect line below has been removed.
                    result = agent.invoke({"input": prompt})
                    response = result["output"]
                    st.markdown(response)
                except Exception as e:
                    response = f"Sorry, an error occurred: {e}"
                    st.error(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()