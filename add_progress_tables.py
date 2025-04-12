import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Database file
DB_FILE = 'enginsync.db'

# Create database if it doesn't exist
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Add progress tracking tables
def create_progress_tables():
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

# Add sample data
def insert_sample_data():
    # First, check if we have users
    cursor.execute("SELECT COUNT(*) FROM Users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Create a sample user if none exists
        cursor.execute(
            "INSERT INTO Users (email, password_hash, full_name) VALUES (?, ?, ?)",
            ("student@example.com", generate_password_hash("password"), "John Doe")
        )
        user_id = cursor.lastrowid
        
        # Add user settings
        cursor.execute(
            "INSERT INTO UserSettings (user_id, theme_preference, notification_prefs) VALUES (?, ?, ?)",
            (user_id, "system", json.dumps({"email_notifications": True}))
        )
    else:
        # Get the first user ID
        cursor.execute("SELECT user_id FROM Users LIMIT 1")
        user_id = cursor.fetchone()[0]
    
    # Sample courses
    courses = [
        ("Calculus I", "Introduction to calculus concepts", "Intermediate", 10),
        ("Linear Algebra", "Fundamentals of linear algebra", "Intermediate", 8),
        ("Thermodynamics", "Principles of thermodynamics", "Advanced", 12),
        ("Statics", "Fundamentals of static mechanics", "Intermediate", 7),
        ("Programming Fundamentals", "Introduction to programming", "Beginner", 15),
        ("Circuit Analysis", "Basic analysis of electrical circuits", "Intermediate", 9)
    ]
    
    # Only insert courses if none exist
    cursor.execute("SELECT COUNT(*) FROM Courses")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Courses (title, description, difficulty_level, total_modules) VALUES (?, ?, ?, ?)",
            courses
        )
    
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
    
    # Only insert skills if none exist
    cursor.execute("SELECT COUNT(*) FROM Skills")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Skills (name, category) VALUES (?, ?)",
            skills
        )
    
    # Get skill IDs
    cursor.execute("SELECT skill_id FROM Skills")
    skill_ids = [row[0] for row in cursor.fetchall()]
    
    # User progress data
    cursor.execute("SELECT COUNT(*) FROM UserProgress")
    if cursor.fetchone()[0] == 0:
        for course_id in course_ids:
            # Random progress for each course
            completion = random.randint(30, 95)
            modules = cursor.execute("SELECT total_modules FROM Courses WHERE course_id = ?", (course_id,)).fetchone()[0]
            modules_completed = int(modules * completion / 100)
            
            cursor.execute(
                "INSERT INTO UserProgress (user_id, course_id, modules_completed, completion_percentage) VALUES (?, ?, ?, ?)",
                (user_id, course_id, modules_completed, completion)
            )
    
    # User skills data
    cursor.execute("SELECT COUNT(*) FROM UserSkills")
    if cursor.fetchone()[0] == 0:
        for skill_id in skill_ids:
            # Random proficiency for each skill
            proficiency = random.randint(40, 90)
            
            cursor.execute(
                "INSERT INTO UserSkills (user_id, skill_id, proficiency_level) VALUES (?, ?, ?)",
                (user_id, skill_id, proficiency)
            )
    
    # User goals data
    cursor.execute("SELECT COUNT(*) FROM UserGoals")
    if cursor.fetchone()[0] == 0:
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
    
    # User activities data
    cursor.execute("SELECT COUNT(*) FROM Activities")
    if cursor.fetchone()[0] == 0:
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

# Execute database setup
create_progress_tables()
insert_sample_data()

# Commit changes and close connection
conn.commit()
conn.close()

print("Progress tracking tables and sample data added successfully!")
