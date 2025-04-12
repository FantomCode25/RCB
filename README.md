# 🚀 EnginSync:Cognitive Nexus

**Team Name:** RCB 
**Date:** 12/04/2025

---

## 📖 Table of Contents

1. [Introduction](#-introduction)
2. [Problem Statement](#-problem-statement)
3. [Solution Overview](#-solution-overview)
4. [Tech Stack](#-tech-stack)
5. [Architecture / Diagram](#-architecture--diagram)
6. [Installation & Usage](#-installation--usage)
7. [Feature Achievements System](#-feature-achievements-system)
8. [Team Members](#-team-members)

---

## 🧠 Introduction

EnginSync:Cognitive Nexus is an AI-powered educational platform designed to enhance students' learning experience through intelligent content processing, interactive learning materials, personalized study planning, and professional development preparation. It serves as a comprehensive assistant that helps students better understand complex materials, prepare for interviews, organize their studies, and track their learning progress.

---

## ❗ Problem Statement

Students face numerous challenges in their educational journey:

1. **Information Overload**: Textbooks and study materials can be overwhelming and difficult to digest efficiently.
2. **Preparation Gap**: Students often lack structured preparation for technical interviews and professional environments.
3. **Study Organization**: Many students struggle with creating effective study plans and organizing their learning materials.
4. **Engagement & Motivation**: Traditional learning methods often fail to keep students engaged over time.
5. **Content Accessibility**: Complex technical content isn't always presented in an accessible, digestible format.

---

## ✅ Solution Overview

RCB Assistant tackles these challenges through a comprehensive suite of AI-powered tools and features:

### Key Features

- **AI-powered PDF Processing & Summarization**: Extract, summarize, and convert text-to-speech from study materials.
- **Interview Preparation System**: Generate personalized interview questions based on uploaded resumes, record and assess answers with AI feedback.
- **Intelligent Study Planning**: AI-generated study plans based on user input and learning goals.
- **YouTube Learning Integration**: Search and integrate relevant educational videos based on study topics.
- **DSA Practice Module**: Organized practice problems for Data Structures and Algorithms with progress tracking.
- **Interactive Dashboard**: Centralized view of learning progress, upcoming tasks, and recommended activities.
- **Voice Interaction**: Record responses and get transcriptions, enabling hands-free learning.

### Unique Value Proposition

EnginSync:Cognitive Nexus combines multiple learning technologies into one cohesive platform, creating a personalized learning experience that adapts to each student's needs, making education more accessible, engaging, and effective.

---

## 🛠️ Tech Stack

- **Frontend:** Flask Templates with HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **AI & ML:** 
  - Google Generative AI (Gemini models)
  - OpenAI API
  - NLTK for Natural Language Processing
  - Whisper for Speech-to-Text
- **APIs / Services:** 
  - YouTube Data API
  - Google Text-to-Speech (gTTS)
  - Adzuna Job Search API
- **Document Processing:** 
  - PyMuPDF (fitz) for PDF handling
  - Markdown for content rendering
- **Audio Processing:** 
  - SoundDevice for audio recording
  - SciPy for audio file operations

---

## 🧩 Architecture / Diagram

EnginSync:Cognitive Nexus follows a modular architecture organized around key functional areas:

```
EnginSync:Cognitive Nexus
│
├── Core Services
│   ├── Authentication & User Management
│   ├── Database Management
│   └── Session Management
│
├── Content Processing Engine
│   ├── PDF Parser & Extractor
│   ├── Text Summarization (NLTK & AI-based)
│   ├── Text-to-Speech Generation
│   └── YouTube Content Integration
│
├── AI Interaction Layer
│   ├── Gemini Models Integration
│   ├── OpenAI Integration
│   ├── Voice Recording & Processing
│   └── Speech-to-Text Transcription
│
├── Learning Management
│   ├── Study Plan Generation
│   ├── Progress Tracking
│   ├── DSA Practice System
│   └── Achievements System
│
└── Career Development Tools
    ├── Interview Preparation System
    ├── Resume Analysis
    ├── Answer Assessment
    └── Job Search Integration
```

---

## 🧪 Installation & Usage

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)
- Dependencies listed in `requirements.txt`

### Steps

```bash
# Clone the repository
git clone https://github.com/FantomCode25/RCB.git

# Navigate into the project directory
cd RCB_FC

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# Create a .env file with your API keys:
# GEMINI_API_KEY=your_gemini_api_key
# OPENAI_API_KEY=your_openai_api_key
# YOUTUBE_API_KEY=your_youtube_api_key

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

---

## 👥 Team Members

- Pavithra C - Lead Developer and Frontend Developer
- Niranjan MS - Developer and Backend Developer
- Mishael Abhishek - Developer and Backend Developer
- Sahana Jain - Tester and QA Engineer
- Team RCB

---

*This README is maintained by the RCB*
