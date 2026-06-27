# mcp-sqlite-chat

A local AI chat interface that lets you query and manage a SQLite database using plain English.

Built with **MCP (Model Context Protocol)** + **Groq** (free LLM). You type natural language questions; the LLM decides which database tools to call; results come back as clean, readable answers.

---

## How It Works

```
You type a question
        │
        ▼
Groq LLM (llama-3.1-8b-instant)
decides which tools to call
        │
        ▼
MCP Client  ──────────>  MCP Server (server.py)
                                  │
                                  ▼
                            Runs SQL on users.db
        <──────────           Returns result
        │
        ▼
Groq formats a human-readable answer
        │
        ▼
"There are 2 users from London."
```

The LLM never touches the database directly — all SQL runs through the MCP server.

---

## Project Structure

```
mcp-sqlite-chat/
  server.py       — MCP server: exposes the SQLite DB as tools and resources
  client.py       — Chat interface: connects to the MCP server and Groq
  init_db.py      — Creates users.db with sample data
  inspect.py      — Utility to inspect the database directly
  users.db        — SQLite database (generated after running init_db.py)
  requirements.txt
  .env.example
```

---

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv /home/abdu/Projects/ai-bot/mcp_1/venv
source /home/abdu/Projects/ai-bot/mcp_1/venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your Groq API key

Copy the example env file and fill in your key:

```bash
cp .env.example .env
```

Edit `.env`:

```
GROQ_API_KEY=your-groq-api-key-here
```

Get a free key at https://console.groq.com

### 4. Initialize the database

```bash
python init_db.py
```

Expected output:
```
Database created at: .../users.db
  - 8 users inserted
  - 10 orders inserted
```

---

## Running

```bash
# Make sure the venv is active
source /home/abdu/Projects/ai-bot/mcp_1/venv/bin/activate

# Start the chat
python client.py
```

You will see:
```
Connecting to SQLite MCP server...
Connected. Tools available: ['list_tables', 'describe_table', 'run_query', 'insert_user', 'insert_order']
--------------------------------------------------
SQLite Chat — type your question or 'quit' to exit
--------------------------------------------------

You:
```

---

## Example Queries

**Explore the schema**
```
You: what tables exist?
You: describe the users table
You: what columns does orders have?
```

**Query users**
```
You: show all users
You: how many users are from London?
You: who is the youngest user?
You: list users older than 30
```

**Query orders**
```
You: show all orders
You: what did Bob order?
You: show all orders over $300
You: what is the total revenue?
```

**Join queries**
```
You: who spent the most money in total?
You: show each user and how much they spent
You: which city's users spend the most?
```

**Insert data**
```
You: add user Sara, sara@gmail.com, age 25, from Paris
You: add an order for alice@example.com for a Monitor costing 349.99
```

Type `quit`, `exit`, or `q` to leave. `Ctrl+C` also works.

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_tables` | Lists all tables in the database |
| `describe_table(table_name)` | Shows columns and types for a table |
| `run_query(sql)` | Runs a SELECT query and returns rows |
| `insert_user(name, email, age, city)` | Adds a new user |
| `insert_order(user_email, product, amount)` | Adds an order for an existing user |

`run_query` is read-only — only SELECT statements are allowed. All writes go through `insert_user` and `insert_order`, which use parameterized queries.

---

## Tech Stack

- [MCP (Model Context Protocol)](https://modelcontextprotocol.io) — tool/resource protocol connecting the client to the server
- [Groq](https://console.groq.com) — free, fast LLM inference (`llama-3.1-8b-instant`)
- [FastMCP](https://github.com/jlowin/fastmcp) — Python framework for building MCP servers
- SQLite — local database, no server needed
