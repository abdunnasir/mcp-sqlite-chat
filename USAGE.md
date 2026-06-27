# SQLite MCP Chat — Usage Guide

A local AI chat interface that lets you query and manage a SQLite database using plain English.
Built with MCP (Model Context Protocol) + Groq (free LLM).

---

## Project Structure

```
sqlite_mcp/
  init_db.py   — creates users.db with sample data
  server.py    — MCP server (exposes DB as tools + resources)
  client.py    — chat interface (you talk to this)
  users.db     — SQLite database (generated after init)
  USAGE.md     — this file
```

---

## Setup (One Time)

### 1. Create and activate virtual environment

```bash
python3 -m venv /home/abdu/Projects/ai-bot/mcp_1/venv
source /home/abdu/Projects/ai-bot/mcp_1/venv/bin/activate
```

### 2. Install dependencies

```bash
pip install mcp groq python-dotenv
```

### 3. Add your Groq API key

Copy from rag-study or create a `.env` file in `mcp_1/`:

```bash
cp /home/abdu/Projects/ai-bot/rag-study/.env /home/abdu/Projects/ai-bot/mcp_1/.env
```

Or manually create `mcp_1/.env`:

```
GROQ_API_KEY=your-groq-key-here
```

Get a free key at: https://console.groq.com

### 4. Create the database

```bash
cd /home/abdu/Projects/ai-bot/mcp_1
python sqlite_mcp/init_db.py
```

Output:
```
Database created at: .../sqlite_mcp/users.db
  - 8 users inserted
  - 10 orders inserted
```

---

## Running the App

```bash
# Activate venv (every new terminal)
source /home/abdu/Projects/ai-bot/mcp_1/venv/bin/activate

# Start the chat
python sqlite_mcp/client.py
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

## What You Can Ask

### Querying Users

```
You: show all users
You: what is alice's email?
You: how many users are from London?
You: show all users from New York
You: who is the youngest user?
You: list users older than 30
```

### Querying Orders

```
You: show all orders
You: what did Bob order?
You: show all orders over $300
You: which product was ordered the most?
You: what is the total revenue?
```

### Joining Users and Orders

```
You: who spent the most money in total?
You: show each user and how much they spent
You: which city's users spend the most?
You: show users who ordered a laptop
```

### Adding Data

```
You: add user Sara, sara@gmail.com, age 25, from Paris
You: add an order for alice@example.com for a Monitor costing 349.99
```

### Exploring the Schema

```
You: what tables exist?
You: describe the users table
You: what columns does orders have?
```

---

## Available Tools (MCP Server)

| Tool | What it does |
|------|-------------|
| `list_tables` | Lists all tables in the database |
| `describe_table(table_name)` | Shows columns and types of a table |
| `run_query(sql)` | Runs a SELECT query and returns rows |
| `insert_user(name, email, age, city)` | Adds a new user |
| `insert_order(user_email, product, amount)` | Adds an order for a user |

> `run_query` is **read-only** — only SELECT statements are allowed.
> All writes go through `insert_user` / `insert_order` which use parameterized queries (no SQL injection).

---

## Sample Database

### users table

| id | name | email | age | city |
|----|------|-------|-----|------|
| 1 | Alice Johnson | alice@example.com | 29 | London |
| 2 | Bob Smith | bob@example.com | 34 | New York |
| 3 | Carlos Diaz | carlos@example.com | 25 | Madrid |
| 4 | Diana Prince | diana@example.com | 31 | Berlin |
| 5 | Ethan Hunt | ethan@example.com | 40 | London |
| 6 | Fatima Malik | fatima@example.com | 27 | Dubai |
| 7 | George Chen | george@example.com | 22 | Singapore |
| 8 | Hannah Brown | hannah@example.com | 35 | New York |

### orders table

| user | product | amount |
|------|---------|--------|
| Alice | Laptop | $999.99 |
| Alice | Mouse | $29.99 |
| Bob | Keyboard | $79.99 |
| Carlos | Monitor | $349.99 |
| Diana | Headphones | $199.99 |
| Ethan | Laptop | $999.99 |
| Fatima | Webcam | $89.99 |
| George | Desk Chair | $449.99 |
| Hannah | Laptop | $999.99 |
| Bob | Monitor | $349.99 |

---

## How It Works Internally

```
You type a question
        │
        ▼
Groq (llama-3.1-8b-instant)
decides which tools to call
        │
        ▼
MCP Client sends tool request
──────────────────────────────> MCP Server (server.py)
                                        │
                                        ▼
                                  Runs SQL on users.db
<──────────────────────────────         │
        │                         Returns result
        ▼
Groq reads result,
formats a human answer
        │
        ▼
Prints: "There are 2 users from London."
```

The LLM never touches the database directly.
The MCP server is the only thing that talks to SQLite.

---

## Quitting

```
You: quit
You: exit
You: q
```

Or press `Ctrl+C`.
