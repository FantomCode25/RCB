import sqlite3

conn = sqlite3.connect('enginsync.db')
cursor = conn.cursor()

# Get UserGoals table schema
cursor.execute("PRAGMA table_info(UserGoals)")
columns = cursor.fetchall()
print("\nUserGoals Table Schema:")
for col in columns:
    print(f"Column {col[0]}: {col[1]} ({col[2]})")

conn.close()
