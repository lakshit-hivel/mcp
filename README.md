# 🤖 LangGraph Chatbot with MCP

This project implements a chatbot using LangGraph that interacts with a Model Context Protocol (MCP) server to query a PostgreSQL database. It leverages an LLM (GPT-4o-mini) to generate responses and MCP tools to access and retrieve information, providing a conversational interface to database functionalities.

## 🚀 Key Features

- **Database Querying via Chat:** Allows users to query a PostgreSQL database using natural language through a chatbot interface.
- **MCP Server Interaction:** Communicates with an MCP server (`pr_mcp_server.py`) to access database querying tools.
- **LangGraph Orchestration:** Uses LangGraph to manage the conversation flow and tool execution.
- **LLM-Powered Responses:** Employs an LLM (GPT-4o-mini) to generate intelligent and context-aware responses.
- **Tool Execution:** Dynamically executes MCP tools based on LLM-generated tool calls.
- **Asynchronous Operations:** Utilizes asynchronous operations for non-blocking communication with the MCP server.
- **Schema Exploration:** Provides tools to explore the database schema, including listing tables and retrieving table schemas.

## 🛠️ Tech Stack

- **Frontend:** N/A (Backend service)
- **Backend:** Python
- **Database:** PostgreSQL
- **AI/LLM:**
  - `langchain_openai` (OpenAI LLMs)
- **Frameworks/Libraries:**
  - `langgraph`
  - `langchain`
  - `mcp` (Message Control Protocol)
  - `psycopg2`
  - `httpx`
- **Other:**
  - `json`
  - `os`
  - `typing`
  - `asyncio`
  - `dotenv`
- **Build Tools:** N/A

## 📦 Getting Started

### Prerequisites

- Python 3.7+
- PostgreSQL database
- OpenAI API key
- MCP installed (`pip install mcp`)
- Other dependencies listed in `requirements.txt`

### Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configure environment variables:

    - Create a `.env` file in the root directory.
    - Add the following variables, replacing the placeholders with your actual values:

    ```
    OPENAI_API_KEY=<your_openai_api_key>
    DATABASE_URL="postgresql://<user>:<password>@<host>:<port>/<database>"
    ```

### Running Locally

1.  Run the chatbot:

    ```bash
    python langgraph/chatbot.py
    ```

## 💻 Usage

Once the chatbot is running, you can interact with it through the console. The chatbot will use the LLM and MCP tools to answer your questions about the database.

Example questions:

- "What is the summary of pull request with ID 123?"
- "List all tables in the insightly schema."
- "What is the schema of the pull_request table?"

## 📂 Project Structure

```
├── langgraph/
│   └── chatbot.py          # LangGraph chatbot implementation
├── pr_mcp_server.py      # MCP server for database access
├── requirements.txt      # Project dependencies
├── README.md               # This file
└── .env                    # Environment variables (API keys, database credentials)
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive messages.
4.  Submit a pull request.

## 📬 Contact

If you have any questions or suggestions, feel free to contact me at [lakshti@hivel.ai](mailto:lakshti@hivel.ai).

## 💖 Thanks

Thanks for checking out this project! I hope it's helpful.

This README is written by [readme.ai](https://readme-generator-phi.vercel.app/), your go-to AI README generator.
