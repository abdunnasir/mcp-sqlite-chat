"""
Run this once to create the database with sample data.
  python init_db.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            age       INTEGER,
            city      TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS orders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER REFERENCES users(id),
            product    TEXT NOT NULL,
            amount     REAL NOT NULL,
            ordered_at TEXT DEFAULT (datetime('now'))
        );
    """)

    users = [
        ("Alice Johnson",  "alice@example.com",  29, "London"),
        ("Bob Smith",      "bob@example.com",    34, "New York"),
        ("Carlos Diaz",    "carlos@example.com", 25, "Madrid"),
        ("Diana Prince",   "diana@example.com",  31, "Berlin"),
        ("Ethan Hunt",     "ethan@example.com",  40, "London"),
        ("Fatima Malik",   "fatima@example.com", 27, "Dubai"),
        ("George Chen",    "george@example.com", 22, "Singapore"),
        ("Hannah Brown",   "hannah@example.com", 35, "New York"),
    ]

    cur.executemany(
        "INSERT OR IGNORE INTO users (name, email, age, city) VALUES (?, ?, ?, ?)",
        users
    )

    orders = [
        (1, "Laptop",     999.99),
        (1, "Mouse",       29.99),
        (2, "Keyboard",    79.99),
        (3, "Monitor",    349.99),
        (4, "Headphones", 199.99),
        (5, "Laptop",     999.99),
        (6, "Webcam",      89.99),
        (7, "Desk Chair", 449.99),
        (8, "Laptop",     999.99),
        (2, "Monitor",    349.99),
    ]

    cur.executemany(
        "INSERT INTO orders (user_id, product, amount) VALUES (?, ?, ?)",
        orders
    )

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")
    print(f"  - {len(users)} users inserted")
    print(f"  - {len(orders)} orders inserted")

if __name__ == "__main__":
    init()
