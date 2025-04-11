import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('enginsync.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT user_id, email FROM Users")
users = cursor.fetchall()

# Fake data generation helpers
def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

# Define some skills for users with categories
skills = [
    ("Python Programming", "Programming", random.randint(65, 95)),
    ("Data Analysis", "Data Science", random.randint(50, 90)),
    ("Machine Learning", "Data Science", random.randint(40, 85)),
    ("Web Development", "Programming", random.randint(55, 95)),
    ("Database Design", "Data Engineering", random.randint(45, 90)),
    ("Software Testing", "Software Engineering", random.randint(60, 90)),
    ("Project Management", "Professional", random.randint(50, 85)),
    ("Cloud Computing", "DevOps", random.randint(40, 80)),
    ("DevOps", "DevOps", random.randint(35, 75)),
    ("UI/UX Design", "Design", random.randint(30, 80)),
]

# Define some course IDs
courses = range(1, 6)

# Define activity types
activity_types = ["exercise", "assignment", "quiz", "project", "reading"]

# Define status types
status_types = ["completed", "in_progress", "graded", "pending"]

# Define goal titles
goal_templates = [
    "Complete {} Module {}",
    "Master {} concepts",
    "Build a {} project",
    "Read {} textbook",
    "Finish {} assignment",
    "Practice {} problems"
]

subjects = ["Python", "Data Science", "Machine Learning", "Web Development", 
            "Database", "Algorithms", "Mathematics", "Statistics"]

print("Adding fake data for users:")

for user in users:
    user_id = user['user_id']
    email = user['email']
    print(f"Processing user {email} (ID: {user_id})")

    # Clear existing data for this user to avoid duplicates
    cursor.execute("DELETE FROM UserSkills WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM UserGoals WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM Activities WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM UserProgress WHERE user_id = ?", (user_id,))

    # 1. Add skills with random proficiency levels
    user_skills = random.sample(skills, random.randint(4, 8))
    for i, (skill_name, category, proficiency) in enumerate(user_skills):
        # Check if skill exists, if not create it
        cursor.execute("SELECT skill_id FROM Skills WHERE name = ?", (skill_name,))
        skill = cursor.fetchone()
        if skill:
            skill_id = skill['skill_id']
        else:
            cursor.execute("INSERT INTO Skills (name, category) VALUES (?, ?)", 
                           (skill_name, category))
            skill_id = cursor.lastrowid

        # Add user's skill level
        cursor.execute("""
            INSERT INTO UserSkills (user_id, skill_id, proficiency_level) 
            VALUES (?, ?, ?)
        """, (user_id, skill_id, proficiency))

    # 2. Add goals with deadlines and progress
    num_goals = random.randint(3, 6)
    for i in range(num_goals):
        subject = random.choice(subjects)
        template = random.choice(goal_templates)
        title = template.format(subject, random.randint(1, 5) if "{}" in template else "")
        
        # Random deadline between today and 30 days from now
        days_offset = random.randint(-5, 30)  # Some goals in the past, some in future
        deadline = datetime.now() + timedelta(days=days_offset)
        
        # Random progress
        progress = random.randint(0, 100)
        is_completed = 1 if progress == 100 else 0
        
        cursor.execute("""
            INSERT INTO UserGoals (user_id, title, progress_percentage, deadline, is_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, progress, deadline, is_completed))

    # 3. Add activities
    num_activities = random.randint(15, 30)
    now = datetime.now()
    
    for i in range(num_activities):
        activity_type = random.choice(activity_types)
        
        # Generate descriptions based on activity type
        if activity_type == "exercise":
            description = f"{random.choice(subjects)} Practice {random.randint(1, 10)}"
        elif activity_type == "assignment":
            description = f"Assignment {random.randint(1, 8)}: {random.choice(subjects)}"
        elif activity_type == "quiz":
            description = f"{random.choice(subjects)} Quiz {random.randint(1, 5)}"
        elif activity_type == "project":
            description = f"{random.choice(subjects)} Project"
        else:
            description = f"Reading on {random.choice(subjects)}"
        
        # Random duration between 15 and 120 minutes
        duration = random.randint(15, 120)
        
        # Random date within last 30 days
        activity_date = now - timedelta(days=random.randint(0, 30), 
                                       hours=random.randint(0, 23), 
                                       minutes=random.randint(0, 59))
        
        # Status
        status = random.choice(status_types)
        
        # Score (if graded)
        score = None
        if status == "graded":
            score = random.randint(65, 100)
        
        cursor.execute("""
            INSERT INTO Activities (user_id, activity_type, description, duration_minutes, 
                                   score, status, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, activity_type, description, duration, score, status, activity_date))

    # 4. Add progress data for courses
    for course_id in courses:
        completed_modules = random.randint(0, 10)
        last_activity = now - timedelta(days=random.randint(0, 14))
        completion_percentage = random.randint(0, 100)
        
        cursor.execute("""
            INSERT INTO UserProgress (user_id, course_id, modules_completed, 
                                    last_activity, completion_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, course_id, completed_modules, last_activity, completion_percentage))

# Commit changes and close connection
conn.commit()
print("\nFake data has been added successfully!")
conn.close()
