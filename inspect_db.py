import sqlite3
import os

DB_FILE = 'enginsync.db'

# Check if database exists
if not os.path.exists(DB_FILE):
    print(f"Database file '{DB_FILE}' not found.")
    exit()

# Connect to database
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [table[0] for table in tables])

# For each table, get its schema
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\nTable: {table_name}")
    print("Columns:", [col[1] for col in columns])

conn.close()
