import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Finance Agent", page_icon="💰", layout="centered")

# --- SETUP AND CACHING ---
# Load environment variables
load_dotenv()

# Define paths and model names
DB_FAISS_PATH = "C:/Users/Rohan/Projects/Project_8/FinancialAgent/faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gemini-1.5-flash"

# Define the custom prompt template
custom_prompt_template = """
Use the following pieces of information to answer the user's question accurately.
You are a personal financial assistant. Your answers should be helpful, clear, and based only on the provided context.
If you don't know the answer from the context, just say that you don't have enough information; don't try to make up an answer.

Context: {context}
Question: {question}

Helpful answer:
"""

@st.cache_resource
def get_qa_chain():
    """
    Creates and returns the RetrievalQA chain. The @st.cache_resource decorator
    ensures this expensive operation runs only once.
    """
    # 1. Initialize the embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )

    # 2. Load the FAISS vector store
    db = FAISS.load_local(
        DB_FAISS_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )

    # 3. Create a retriever
    retriever = db.as_retriever(search_kwargs={'k': 3})

    # 4. Initialize the LLM
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.7)
    
    # 5. Create the prompt from the template
    prompt = PromptTemplate(
        template=custom_prompt_template,
        input_variables=['context', 'question']
    )

    # 6. Create and return the QA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={'prompt': prompt}
    )
    return chain

# --- UI AND INTERACTION ---
st.title("💰 AI Finance Agent")
st.write("Welcome! Ask questions about your financial data.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help with your finances today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get an instance of the QA chain
qa_chain = get_qa_chain()

# Handle user input
if prompt := st.chat_input("Ask about your transactions, stocks, or funds..."):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = qa_chain.invoke({"query": prompt})
            response = result['result']
            st.markdown(response)
            
    # Add AI response to history
    st.session_state.messages.append({"role": "assistant", "content": response})