# 🏆 AI Finance Agent: Conversational Financial Insights

*An advanced, multi-tool AI agent that provides a conversational interface for personal financial data, featuring dynamic data syncing, on-demand visualizations, and proactive analysis.*

---

<p align="center">
  <a href="[Link-to-Your-Live-Demo-URL]">
    <img src="https://img.shields.io/badge/Live_Demo-🚀-blue?style=for-the-badge" alt="Live Demo">
  </a>
  <a href="[Link-to-Your-LinkedIn-Profile]">
    <img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn Profile">
  </a>
</p>

---

## 🏛️ Project Architecture

The application is built on a modern, agent-based architecture. The Streamlit frontend provides the user interface, which communicates with a backend agent orchestrated by LangChain. The agent, powered by Google Gemini, intelligently decides which tool to use based on the user's query to provide accurate, context-aware responses.

```mermaid
graph TD
    %% ==== USER INTERFACE ====
    subgraph UI[User Interface]
        A[User] --> B[Streamlit UI]
    end

    %% ==== BACKEND LOGIC ====
    subgraph Backend[Backend Logic]
        B --> C{Authentication}
        C -- Authenticated --> D[LangChain Executor]
    end

    %% ==== AI CORE (HERO) ====
    subgraph AI[AI Core]
        D --> E[Google Gemini LLM]
        E -- Tool Selection --> D
    end

    %% ==== AGENT TOOLS ====
    subgraph Tools[Agent Tools]
        D --> F[SQL Database Toolkit]
        D --> G[Visualization Tool]
    end

    %% ==== DATA LAYER ====
    subgraph Data[Data Layer]
        F --> H[(SQLite Database)]
        G --> H
        I[Plaid API] --> H
    end

    %% ==== STYLING ====
    %% Neutral greys for most layers
    style UI fill:#f5f5f5,stroke:#444,color:#000
    style Backend fill:#f5f5f5,stroke:#444,color:#000
    style Tools fill:#f5f5f5,stroke:#444,color:#000
    style Data fill:#f5f5f5,stroke:#444,color:#000

    %% Hero (AI Core) highlighted in teal
    style AI fill:#00b4d8,stroke:#006d77,stroke-width:2px,color:#fff

    %% Highlight Gemini LLM node
    style E fill:#00b4d8,stroke:#006d77,stroke-width:2px,color:#fff

    %% Subtle highlight for LangChain Executor (bridge to AI Core)
    style D fill:#e0f7fa,stroke:#444,color:#000

````

-----

## ✨ Key Features

  * **🔐 Secure Multi-User Authentication:** A complete login/logout system with hashed passwords ensures each user's data is private and isolated in a multi-tenant database schema.
  * **🔗 Dynamic Bank Data Syncing:** Integrates with the **Plaid API** (in a sandbox environment) to allow users to link bank accounts and sync real-time transaction data into their personal database.
  * **🧠 Intelligent Multi-Tool Agent:** The core of the application is a sophisticated LangChain agent that can intelligently choose between different tools to answer a user's request.
      * **💬 Conversational Database Querying:** Ask complex questions in natural language (e.g., *"What was my biggest expense last month?"*). The agent translates the query into SQL, executes it, and provides a natural language response.
      * **📊 On-Demand Data Visualization:** Request visual breakdowns of spending (e.g., *"Show me a pie chart of my expenses"*). The agent uses a custom tool to generate interactive charts with Plotly, which are displayed directly in the chat.
  * **💡 Proactive Financial Summaries:** Generate a one-click financial summary where the agent proactively asks and answers key analytical questions about spending habits and important metrics.

-----

## 🕹️ How to Use the Live Demo

1.  **Login:** Use the test credentials:
      * **Username:** `jsmith`
      * **Password:** `123`
2.  **Sync Data:** After logging in, expand the **"Sync Bank Transactions"** section and click the button to load sample data into the account.
3.  **Interact:** Start asking questions or generating reports\!

#### Example Prompts:

  * `What was my total spending in the last 30 days?`
  * `Show me a pie chart of my expenses.`
  * Click the **"Generate Financial Summary"** button for a full report.

-----

## 💻 Tech Stack

| Category         | Technology / Library                               |
| ---------------- | -------------------------------------------------- |
| **AI & Backend** | LangChain, Google Gemini, Pandas                   |
| **Frontend** | Streamlit                                          |
| **Database** | SQLite                                             |
| **API & Services**| Plaid API                                          |
| **Visualization**| Plotly                                             |
| **Authentication**| Streamlit Authenticator                            |
| **Testing** | Pytest                                             |
| **Deployment** | Docker                                             |

-----

## 🔧 Running Locally

**Prerequisites:** Python 3.11+, Git, Docker Desktop.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)
    cd YourRepoName
    ```
2.  **Set Up Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Configure Credentials:**
      * Create a `.env` file and add your API keys (`GOOGLE_API_KEY`, `PLAID_CLIENT_ID`, `PLAID_SECRET`).
      * Create a `config.yaml` file for user credentials. Use `generate_keys.py` to create hashed passwords.
4.  **Initialize the Database:**
    ```bash
    python create_database.py
    ```
5.  **Run the Application with Streamlit:**
    ```bash
    streamlit run app.py
    ```
6.  **Run with Docker (Optional):**
    ```bash
    # Build the image
    docker build -t finance-agent .
    # Run the container
    docker run -p 8501:8501 --env-file .env finance-agent
    ```

<!-- end list -->

```
```
