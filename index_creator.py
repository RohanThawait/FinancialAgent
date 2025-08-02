import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables from .env file
load_dotenv()

# Define paths
DATA_PATH = "data"
DB_FAISS_PATH = "faiss_index"

def load_financial_documents():
    """Loads all CSV documents from the data directory."""
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.csv",
        loader_cls=CSVLoader,
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()
    return documents

def create_vector_store(documents):
    """Splits documents, creates embeddings, and stores them in a FAISS vector store."""
    print("\nSplitting documents into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    print(f"✅ Split {len(documents)} documents into {len(docs)} chunks.")

    print("\nLoading HuggingFace embedding model...")
    # We use a powerful, lightweight model for creating embeddings.
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}  # Use CPU for broad compatibility
    )
    print("✅ Embedding model loaded.")

    print("\nCreating and saving the FAISS vector store...")
    # Create the FAISS vector store from the document chunks and embeddings.
    db = FAISS.from_documents(docs, embeddings)
    
    # Save the vector store locally.
    db.save_local(DB_FAISS_PATH)
    print(f"✅ Vector store created and saved to '{DB_FAISS_PATH}' folder.")
    return db

def main():
    """Main function to load docs and create the vector store."""
    loaded_docs = load_financial_documents()
    
    if loaded_docs:
        print(f"\n✅ Successfully loaded {len(loaded_docs)} documents.")
        create_vector_store(loaded_docs)
    else:
        print("❌ Document loading failed. Cannot create vector store.")

if __name__ == "__main__":
    main()