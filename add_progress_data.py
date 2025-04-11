import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

# Database file
DB_FILE = 'enginsync.db'

# Connect to database
conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
cursor = conn.cursor()

# Create fresh progress tables
def create_progress_tables():
    # Drop existing tables if they exist
    tables_to_drop = ['Skills', 'Courses', 'UserProgress', 'UserSkills', 'UserGoals', 'Activities']
    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # Skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT
    )
    ''')
    
    # Courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        difficulty_level TEXT,
        total_modules INTEGER DEFAULT 0
    )
    ''')
    
    # UserProgress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserProgress (
        progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        modules_completed INTEGER DEFAULT 0,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completion_percentage REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES Users (user_id),
        FOREIGN KEY (course_id) REFERENCES Courses (course_id)
    )
    ''')
    
    # UserSkills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserSkills (
        user_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        proficiency_level REAL DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (user_id),
        FOREIGN KEY (skill_id) REFERENCES Skills (skill_id)
    )
    ''')
    
    # UserGoals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserGoals (
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        progress_percentage REAL DEFAULT 0,
        deadline TIMESTAMP,
        is_completed BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES Users (user_id)
    )
    ''')
    
    # Activities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Activities (
        activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        activity_type TEXT NOT NULL,
        description TEXT NOT NULL,
        duration_minutes INTEGER,
        score REAL,
        status TEXT,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (user_id)
    )
    ''')

# Insert sample data for the current user
def insert_sample_data():
    # Get existing user ID
    try:
        cursor.execute("SELECT user_id FROM Users LIMIT 1")
        user_id = cursor.fetchone()[0]
        print(f"Found user ID: {user_id}")
    except:
        print("No users found in the database.")
        return
    
    # Sample courses
    courses = [
        ("Calculus I", "Introduction to calculus concepts", "Intermediate", 10),
        ("Linear Algebra", "Fundamentals of linear algebra", "Intermediate", 8),
        ("Thermodynamics", "Principles of thermodynamics", "Advanced", 12),
        ("Statics", "Fundamentals of static mechanics", "Intermediate", 7),
        ("Programming Fundamentals", "Introduction to programming", "Beginner", 15),
        ("Circuit Analysis", "Basic analysis of electrical circuits", "Intermediate", 9)
    ]
    
    cursor.executemany(
        "INSERT INTO Courses (title, description, difficulty_level, total_modules) VALUES (?, ?, ?, ?)",
        courses
    )
    print("Courses added.")
    
    # Get course IDs
    cursor.execute("SELECT course_id FROM Courses")
    course_ids = [row[0] for row in cursor.fetchall()]
    
    # Sample skills
    skills = [
        ("Calculus", "Mathematics"),
        ("Linear Algebra", "Mathematics"),
        ("Thermodynamics", "Physics"),
        ("Statics", "Engineering"),
        ("Programming", "Computer Science"),
        ("Circuits", "Electrical Engineering")
    ]
    
    cursor.executemany(
        "INSERT INTO Skills (name, category) VALUES (?, ?)",
        skills
    )
    print("Skills added.")
    
    # Get skill IDs
    cursor.execute("SELECT skill_id FROM Skills")
    skill_ids = [row[0] for row in cursor.fetchall()]
    
    # User progress data
    for course_id in course_ids:
        # Random progress for each course
        completion = random.randint(30, 95)
        modules = cursor.execute("SELECT total_modules FROM Courses WHERE course_id = ?", (course_id,)).fetchone()[0]
        modules_completed = int(modules * completion / 100)
        
        cursor.execute(
            "INSERT INTO UserProgress (user_id, course_id, modules_completed, completion_percentage) VALUES (?, ?, ?, ?)",
            (user_id, course_id, modules_completed, completion)
        )
    print("User progress added.")
    
    # User skills data
    for skill_id in skill_ids:
        # Random proficiency for each skill
        proficiency = random.randint(40, 90)
        
        cursor.execute(
            "INSERT INTO UserSkills (user_id, skill_id, proficiency_level) VALUES (?, ?, ?)",
            (user_id, skill_id, proficiency)
        )
    print("User skills added.")
    
    # User goals data
    goals = [
        ("Complete Calculus Module 1", 75, datetime.now() + timedelta(days=10), 0),
        ("Read Physics Chapter 4", 90, datetime.now() + timedelta(days=5), 0),
        ("Project: Thermodynamics Sim", 40, datetime.now() + timedelta(days=14), 0)
    ]
    
    for goal in goals:
        cursor.execute(
            "INSERT INTO UserGoals (user_id, title, progress_percentage, deadline, is_completed) VALUES (?, ?, ?, ?, ?)",
            (user_id, goal[0], goal[1], goal[2], goal[3])
        )
    print("User goals added.")
    
    # User activities data
    now = datetime.now()
    activities = [
        ("assignment", "Calculus Practice Problems (Set 3)", 45, None, "completed", now - timedelta(days=3)),
        ("lecture", "Physics Lecture: Kinematics", 60, None, "watched", now - timedelta(days=4)),
        ("assignment", "Assignment 1: Mechanics", None, 85, "graded", now - timedelta(days=5)),
        ("lab", "Chemistry Lab Simulation", None, None, "pending", now - timedelta(days=6))
    ]
    
    for activity in activities:
        cursor.execute(
            "INSERT INTO Activities (user_id, activity_type, description, duration_minutes, score, status, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, activity[0], activity[1], activity[2], activity[3], activity[4], activity[5])
        )
    print("User activities added.")

# Execute database setup
print("Creating progress tables...")
create_progress_tables()
print("Adding sample data...")
insert_sample_data()

# Calculate overall progress
def calculate_overall_progress():
    cursor.execute("SELECT user_id FROM Users LIMIT 1")
    user_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(completion_percentage) FROM UserProgress WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    overall = result[0] if result and result[0] is not None else 0
    
    print(f"Overall progress: {overall:.2f}%")

calculate_overall_progress()

# Commit changes and close connection
conn.commit()
conn.close()

print("Progress data setup completed successfully!")
