import sqlite3

conn = sqlite3.connect('enginsync.db')
cursor = conn.cursor()

# Check Skills table schema
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Skills'")
table_exists = cursor.fetchone()

if table_exists:
    # Get Skills table schema
    cursor.execute("PRAGMA table_info(Skills)")
    columns = cursor.fetchall()
    print("\nSkills Table Schema:")
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")

    # Show some sample data if available
    cursor.execute("SELECT * FROM Skills LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print("\nSkills Sample Data:")
        print(rows)
else:
    print("\nSkills table does not exist!")

# Check Activities table schema
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Activities'")
table_exists = cursor.fetchone()

if table_exists:
    # Get Activities table schema
    cursor.execute("PRAGMA table_info(Activities)")
    columns = cursor.fetchall()
    print("\nActivities Table Schema:")
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")

    # Show sample data
    cursor.execute("SELECT * FROM Activities LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        print("\nActivities Sample Data:")
        print(rows)
else:
    print("\nActivities table does not exist!")

# Check UserGoals table schema
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UserGoals'")
table_exists = cursor.fetchone()

if table_exists:
    # Get UserGoals table schema
    cursor.execute("PRAGMA table_info(UserGoals)")
    columns = cursor.fetchall()
    print("\nUserGoals Table Schema:")
    for col in columns:
        print(f"Column {col[0]}: {col[1]} ({col[2]})")

    # Show some sample data
    cursor.execute("SELECT * FROM UserGoals LIMIT 3")
    rows = cursor.fetchall()
    if rows:
        print("\nUserGoals Sample Data:")
        print(rows)
else:
    print("\nUserGoals table does not exist!")

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\nAll tables in the database:")
for table in tables:
    print(table[0])

conn.close()
