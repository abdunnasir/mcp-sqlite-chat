"""
MCP Server — wraps a local SQLite database.

Exposes:
  Tools:     list_tables, describe_table, run_query, insert_user, insert_order
  Resources: db://tables, db://users, db://orders
"""
import sqlite3
import json
import os
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

mcp = FastMCP("SQLite Assistant")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


# ─── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_tables() -> str:
    """List all tables in the database."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    tables = [r["name"] for r in rows]
    return json.dumps({"tables": tables})


@mcp.tool()
def describe_table(table_name: str) -> str:
    """Show the columns and types of a table."""
    conn = get_conn()
    try:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        conn.close()
        if not rows:
            return json.dumps({"error": f"Table '{table_name}' not found."})
        columns = [{"name": r["name"], "type": r["type"], "not_null": bool(r["notnull"])} for r in rows]
        return json.dumps({"table": table_name, "columns": columns})
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})


@mcp.tool()
def run_query(sql: str) -> str:
    """
    Run a READ-ONLY SQL query (SELECT only) and return results.
    Do NOT use this for INSERT/UPDATE/DELETE — use insert_user or insert_order instead.
    """
    sql_stripped = sql.strip().upper()
    if not sql_stripped.startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries are allowed via run_query."})

    conn = get_conn()
    try:
        rows = conn.execute(sql).fetchall()
        conn.close()
        results = [dict(r) for r in rows]
        return json.dumps({"count": len(results), "rows": results})
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})


@mcp.tool()
def insert_user(name: str, email: str, age: int, city: str) -> str:
    """Add a new user to the database."""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (name, email, age, city) VALUES (?, ?, ?, ?)",
            (name, email, age, city)
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return json.dumps({"success": True, "user_id": user_id, "message": f"User '{name}' added with id {user_id}."})
    except sqlite3.IntegrityError:
        conn.close()
        return json.dumps({"error": f"Email '{email}' already exists."})
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})


@mcp.tool()
def insert_order(user_email: str, product: str, amount: float) -> str:
    """Add a new order for an existing user (identified by email)."""
    conn = get_conn()
    try:
        user = conn.execute("SELECT id, name FROM users WHERE email = ?", (user_email,)).fetchone()
        if not user:
            conn.close()
            return json.dumps({"error": f"No user found with email '{user_email}'."})

        conn.execute(
            "INSERT INTO orders (user_id, product, amount) VALUES (?, ?, ?)",
            (user["id"], product, amount)
        )
        conn.commit()
        conn.close()
        return json.dumps({"success": True, "message": f"Order '{product}' added for {user['name']}."})
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})


# ─── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("db://tables")
def resource_tables() -> str:
    """Overview of all tables in the database."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()
    return "Tables in database:\n" + "\n".join(f"  - {r['name']}" for r in rows)


@mcp.resource("db://{table_name}")
def resource_table(table_name: str) -> str:
    """Return first 20 rows of a table as a preview."""
    conn = get_conn()
    try:
        rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 20").fetchall()
        conn.close()
        if not rows:
            return f"Table '{table_name}' is empty."
        results = [dict(r) for r in rows]
        return json.dumps(results, indent=2)
    except Exception as e:
        conn.close()
        return f"Error: {e}"


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
