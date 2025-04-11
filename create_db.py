import sqlite3
import os

# Database file path
db_file = 'enginsync.db'

# Remove existing database file if it exists
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Removed existing database file: {db_file}")

# Connect to the database (this will create the file)
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute('PRAGMA foreign_keys = ON;')

# Creating all the tables based on the schema

# 1. User Management Tables
cursor.execute('''
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE UserSettings (
    setting_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    theme_preference TEXT DEFAULT 'system',
    notification_prefs TEXT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

cursor.execute('''
CREATE TABLE LearningStyleAssessments (
    assessment_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    assessment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    primary_style_type TEXT NOT NULL,
    primary_style_label TEXT NOT NULL,
    secondary_style_type TEXT,
    secondary_style_label TEXT,
    raw_scores TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# 2. Document & Bot Interaction Tables
cursor.execute('''
CREATE TABLE UserDocuments (
    document_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    original_filename TEXT,
    upload_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME,
    status TEXT,
    context_id TEXT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

cursor.execute('''
CREATE TABLE BotInteractions (
    interaction_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_id INTEGER,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_query TEXT NOT NULL,
    bot_response_type TEXT NOT NULL,
    bot_response TEXT,
    processing_time_ms INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (document_id) REFERENCES UserDocuments(document_id)
)
''')

# 3. Course Content Structure Tables
cursor.execute('''
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    subject_area TEXT,
    difficulty_level TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE Modules (
    module_id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    module_order INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
)
''')

cursor.execute('''
CREATE TABLE Lessons (
    lesson_id INTEGER PRIMARY KEY,
    module_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    estimated_duration_mins INTEGER,
    lesson_order INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES Modules(module_id)
)
''')

cursor.execute('''
CREATE TABLE LessonContent (
    content_id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    content_data TEXT NOT NULL,
    content_order INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id)
)
''')

cursor.execute('''
CREATE TABLE Quizzes (
    quiz_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE QuizQuestions (
    question_id INTEGER PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    options TEXT,
    correct_answer TEXT,
    points INTEGER DEFAULT 1,
    FOREIGN KEY (quiz_id) REFERENCES Quizzes(quiz_id)
)
''')

# 4. Skills & Progress Tracking Tables
cursor.execute('''
CREATE TABLE Skills (
    skill_id INTEGER PRIMARY KEY,
    skill_name TEXT UNIQUE NOT NULL,
    description TEXT,
    domain TEXT
)
''')

cursor.execute('''
CREATE TABLE LessonSkills (
    lesson_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (lesson_id, skill_id),
    FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id),
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id)
)
''')

cursor.execute('''
CREATE TABLE UserProgress (
    progress_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_started',
    completion_date DATETIME,
    score REAL,
    time_spent_secs INTEGER,
    last_accessed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, lesson_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (lesson_id) REFERENCES Lessons(lesson_id)
)
''')

cursor.execute('''
CREATE TABLE UserSkillMastery (
    user_skill_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    mastery_level REAL NOT NULL,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    evidence TEXT,
    UNIQUE (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (skill_id) REFERENCES Skills(skill_id)
)
''')

# 5. Placement Preparation Tables
cursor.execute('''
CREATE TABLE ResourceCategories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE PlacementResources (
    resource_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    resource_type TEXT NOT NULL,
    url_or_data TEXT NOT NULL,
    difficulty TEXT,
    relevant_skills TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES ResourceCategories(category_id)
)
''')

cursor.execute('''
CREATE TABLE UserSavedResources (
    user_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,
    saved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, resource_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (resource_id) REFERENCES PlacementResources(resource_id)
)
''')

# 6. Gamification Tables
cursor.execute('''
CREATE TABLE Badges (
    badge_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_url TEXT
)
''')

cursor.execute('''
CREATE TABLE Achievements (
    achievement_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    criteria TEXT,
    points_reward INTEGER DEFAULT 0,
    badge_id INTEGER,
    FOREIGN KEY (badge_id) REFERENCES Badges(badge_id)
)
''')

cursor.execute('''
CREATE TABLE UserAchievements (
    user_achievement_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (achievement_id) REFERENCES Achievements(achievement_id)
)
''')

cursor.execute('''
CREATE TABLE UserBadges (
    user_badge_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    awarded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_achievement_id INTEGER,
    UNIQUE (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (badge_id) REFERENCES Badges(badge_id),
    FOREIGN KEY (source_achievement_id) REFERENCES Achievements(achievement_id)
)
''')

cursor.execute('''
CREATE TABLE UserPointsHistory (
    points_log_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    points_change INTEGER NOT NULL,
    reason TEXT,
    related_entity_id INTEGER,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# 7. Notifications Table
cursor.execute('''
CREATE TABLE Notifications (
    notification_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    type TEXT,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    link_url TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# 8. Placement Assessment and Practice Problem Tables

# Categories for placement assessment and problems
cursor.execute('''
CREATE TABLE IF NOT EXISTS placement_categories (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id VARCHAR(36) REFERENCES placement_categories(id),
    order_index INTEGER DEFAULT 0,
    icon_class VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Questions for the placement assessment
cursor.execute('''
CREATE TABLE IF NOT EXISTS placement_questions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    category_id VARCHAR(36) NOT NULL REFERENCES placement_categories(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL, -- 'mcq', 'coding', 'short_answer'
    options JSON,                        -- For MCQ, store options as JSON array
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 10), -- 1-10 scale
    time_estimate_seconds INTEGER,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# User assessments (attempts)
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_placement_assessments (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_questions INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_score FLOAT DEFAULT 0.0,
    results JSON,                        -- Detailed results by category
    question_ids JSON,                   -- List of question IDs in this assessment
    answered_question_ids JSON,          -- List of question IDs that have been answered
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# User answers to assessment questions
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_placement_answers (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    assessment_id VARCHAR(36) NOT NULL,
    question_id VARCHAR(36) NOT NULL,
    user_id INTEGER NOT NULL,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    time_taken_seconds INTEGER,
    points_awarded FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES user_placement_assessments(id),
    FOREIGN KEY (question_id) REFERENCES placement_questions(id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')

# User proficiency levels by category
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_proficiency_levels (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    user_id INTEGER NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    skill_level INTEGER NOT NULL CHECK(skill_level BETWEEN 1 AND 10), -- 1-10 scale
    confidence_score FLOAT, -- How confident we are in this skill level (0-100%)
    source VARCHAR(20) NOT NULL DEFAULT 'assessment', -- 'assessment', 'user_input', 'progress'
    assessment_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES placement_categories(id),
    FOREIGN KEY (assessment_id) REFERENCES user_placement_assessments(id)
)
''')

# Practice problems master list
cursor.execute('''
CREATE TABLE IF NOT EXISTS practice_problems (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    problem_url TEXT NOT NULL,
    solution_url TEXT,
    category_id VARCHAR(36) NOT NULL,
    difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 10), -- 1-10 scale
    source_platform VARCHAR(50), -- 'LeetCode', 'HackerRank', 'Internal', etc.
    tags JSON, -- Array of tags for better filtering
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES placement_categories(id)
)
''')

# Daily recommended problems for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS daily_user_problems (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            substr('89ab',abs(random()) % 4 + 1, 1) || 
            substr(lower(hex(randomblob(2))),2) || '-' || 
            lower(hex(randomblob(6)))),
    user_id INTEGER NOT NULL,
    problem_id VARCHAR(36) NOT NULL,
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'started', 'completed', 'skipped'
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, problem_id, assigned_date),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (problem_id) REFERENCES practice_problems(id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database '{db_file}' created successfully with all tables including placement assessment tables.")
