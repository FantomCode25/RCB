import sqlite3
import os
import sys

# Database file path
db_file = 'enginsync.db'

# Check if database file exists
if not os.path.exists(db_file):
    print(f"Database file not found: {db_file}")
    sys.exit(1)

# Connect to the database
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Get information about the Users table
try:
    # Check Users table schema
    cursor.execute("PRAGMA table_info(Users)")
    columns = cursor.fetchall()
    print("=== Users Table Schema ===")
    for col in columns:
        print(f"{col['name']} ({col['type']})")
    
    # Check sample user data
    cursor.execute("SELECT * FROM Users LIMIT 3")
    users = cursor.fetchall()
    print("\n=== Sample User Data ===")
    for user in users:
        print("User ID:", user['user_id'])
        for key in user.keys():
            print(f"  {key}: {user[key]}")
        print("---")

    # Check if there are any UserPreferences 
    cursor.execute("PRAGMA table_info(UserPreferences)")
    columns = cursor.fetchall()
    if columns:
        print("\n=== UserPreferences Table Schema ===")
        for col in columns:
            print(f"{col['name']} ({col['type']})")
        
        # Sample data
        cursor.execute("SELECT * FROM UserPreferences LIMIT 3")
        prefs = cursor.fetchall()
        print("\n=== Sample UserPreferences Data ===")
        for pref in prefs:
            print(f"User ID: {pref['user_id']}")
            for key in pref.keys():
                print(f"  {key}: {pref[key]}")
            print("---")
    else:
        print("\nUserPreferences table does not exist.")
        
    # Check UserGoals table
    cursor.execute("PRAGMA table_info(UserGoals)")
    columns = cursor.fetchall()
    if columns:
        print("\n=== UserGoals Table Schema ===")
        for col in columns:
            print(f"{col['name']} ({col['type']})")
        
        # Sample data
        cursor.execute("SELECT * FROM UserGoals LIMIT 3")
        goals = cursor.fetchall()
        print("\n=== Sample UserGoals Data ===")
        for goal in goals:
            print(f"User ID: {goal['user_id'] if 'user_id' in goal.keys() else 'unknown'}")
            for key in goal.keys():
                print(f"  {key}: {goal[key]}")
            print("---")
    else:
        print("\nUserGoals table does not exist.")

except sqlite3.Error as e:
    print(f"Database error: {e}")

finally:
    conn.close()
