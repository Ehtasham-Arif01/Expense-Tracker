import sqlite3

# Connect to SQLite Database
conn = sqlite3.connect("expense_tracker.db")
c = conn.cursor()

# Create Users Table
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)""")

# Create Expenses Table
c.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    date TEXT DEFAULT CURRENT_DATE,  -- Automatically stores the system date
    amount REAL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)""")

# Create Income Table
c.execute("""CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    date TEXT DEFAULT CURRENT_DATE,  -- Automatically stores the system date
    source TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)""")

conn.commit()
conn.close()
