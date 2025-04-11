import sqlite3
import os
import json
import functools
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g,
    jsonify, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
import tempfile
from werkzeug.utils import secure_filename
from pdf_utils import process_pdf, text_to_speech
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from string import punctuation
from heapq import nlargest
from openai import OpenAI
import googleapiclient.discovery
import googleapiclient.errors

# --- App Configuration ---
app = Flask(__name__)
# IMPORTANT: Change this to a long, random secret key in a real application
# You can generate one using: python -c 'import os; print(os.urandom(24))'
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', b'_5#y2L"F4Q8z\n\xec]/')
app.config['DATABASE'] = 'enginsync.db'

# Initialize OpenAI client for advanced summarization
openai_api_key = os.environ.get('OPENAI_API_KEY')
client = None
if openai_api_key and openai_api_key != 'your_openai_api_key_here':
    try:
        client = OpenAI(api_key=openai_api_key)
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
else:
    print("OpenAI API key not set or invalid - AI summarization will not be available")

# Add custom template filters
@app.template_filter('strftime')
def format_datetime(value, format='%Y-%m-%d'):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    return value.strftime(format)

# --- Database Helper Functions ---

def get_db():
    """Connects to the specific database."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Helper function to query database."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# --- Authentication Decorator ---

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Load User Hook ---

@app.before_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object """
    """from the database into flask.g.user."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = query_db('SELECT * FROM Users WHERE user_id = ?', [user_id], one=True)
        if g.user is None: # Clear session if user_id is invalid
            session.clear()


# --- Routes ---

@app.route('/')
@app.route('/home')
def home():
    """Public homepage."""
    return render_template('home.html')

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    """User registration."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        full_name = request.form.get('firstName', '').strip() + " " + request.form.get('lastName', '').strip()
        role = 'student'  # Default role since we removed the selection
        terms = request.form.get('terms') # Checkbox value is 'on' if checked

        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
             error = 'Passwords do not match.'
        elif not terms:
             error = 'You must agree to the terms.'
        elif query_db('SELECT user_id FROM Users WHERE email = ?', [email], one=True) is not None:
            error = f"Email '{email}' is already registered."

        if error is None:
            db = get_db()
            try:
                # Create user with role
                user_id = db.execute(
                    "INSERT INTO Users (email, password_hash, full_name) VALUES (?, ?, ?)",
                    (email, generate_password_hash(password), full_name),
                ).lastrowid
                
                # Store user role in UserSettings
                db.execute(
                    "INSERT INTO UserSettings (user_id, theme_preference, notification_prefs) VALUES (?, ?, ?)",
                    (user_id, 'system', json.dumps({'role': role or 'student'}))
                )
                
                db.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.Error as e:
                 error = f"Database error: {e}"
                 db.rollback() # Rollback changes on error

        if error:
             flash(error, 'error')

    # GET request or failed POST
    return render_template('signup.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        error = None
        user = query_db('SELECT * FROM Users WHERE email = ?', [email], one=True)

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['user_id']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('dashboard'))

        flash(error, 'error')

    # GET request or failed POST
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logs the user out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# --- Protected Routes ---

@app.route('/dashboard')
@login_required
def dashboard():
    """Shows the main dashboard after login."""
    # g.user is available here thanks to @app.before_request
    user_id = g.user['user_id']
    
    # Get current datetime for template
    now = datetime.now()
    
    # Fetch user's skills with proficiency levels
    skills = query_db("""
        SELECT s.name, us.proficiency_level 
        FROM UserSkills us
        JOIN Skills s ON us.skill_id = s.skill_id
        WHERE us.user_id = ?
    """, [user_id])
    
    # Fetch user's goals
    goals = query_db("""
        SELECT title, deadline, progress_percentage
        FROM UserGoals
        WHERE user_id = ?
        ORDER BY deadline
    """, [user_id])
    
    # Fetch recent activities
    activities = query_db("""
        SELECT description, completed_at, duration_minutes, score, status
        FROM Activities
        WHERE user_id = ?
        ORDER BY completed_at DESC
        LIMIT 10
    """, [user_id])
    
    # Calculate total exercises completed
    exercise_count = query_db('''
        SELECT COUNT(*) as count
        FROM Activities
        WHERE user_id = ? AND activity_type = 'exercise'
    ''', [user_id], one=True)['count']
    
    # Calculate total hours studied
    hours_result = query_db("""
        SELECT SUM(duration_minutes) as total_minutes
        FROM Activities
        WHERE user_id = ?
    """, [user_id], one=True)
    hours_studied = round(hours_result['total_minutes'] / 60) if hours_result['total_minutes'] else 0
    
    # Weekly progress for chart
    weekly_progress = query_db("""
        SELECT strftime('%W', completed_at) as week, COUNT(*) as count
        FROM Activities
        WHERE user_id = ?
        GROUP BY week
        ORDER BY week
        LIMIT 6
    """, [user_id])
    
    # Get assignment scores for completion chart
    assignments = query_db('''
        SELECT description, score
        FROM Activities
        WHERE user_id = ? AND activity_type = 'assignment' AND score IS NOT NULL
        ORDER BY completed_at DESC
        LIMIT 6
    ''', [user_id])
    
    # Calculate streak (consecutive days with activity)
    streak = 5  # Placeholder - would need more complex query to calculate actual streak
    
    # Calculate overall progress percentage
    overall_progress = query_db("""
        SELECT AVG(completion_percentage) as avg_progress
        FROM UserProgress
        WHERE user_id = ?
    """, [user_id], one=True)['avg_progress'] or 0
    
    return render_template('dashboard.html',
                          user=g.user,
                          full_name=g.user['full_name'],
                          skills=skills,
                          goals=goals,
                          activities=activities,
                          exercise_count=exercise_count,
                          hours_studied=hours_studied,
                          weekly_progress=weekly_progress,
                          assignments=assignments,
                          streak=streak,
                          overall_progress=overall_progress,
                          now=now)

# Courses route removed as requested

# Progress route removed - now integrated into dashboard

@app.route('/planner')
@login_required
def planner():
    """Placeholder for planner page."""
    return render_template('planner.html', back_url=url_for('dashboard'))

@app.route('/jobsearch', methods=['GET', 'POST']) # Renamed from placement.html
@login_required
def jobsearch():
    """Job search page using Adzuna API."""
    jobs = []
    error = None
    user_id = g.user['user_id']
    
    if request.method == 'POST':
        skills = request.form.get('skills', '')
        location = request.form.get('location', 'Karnataka')
        num_results = int(request.form.get('num_results', 5))
        
        # Adzuna API endpoint for India
        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        
        # API parameters
        params = {
            "app_id": "96e12eac",
            "app_key": "7a545dc457029cd2527a9f21a366010e",
            "what": skills,
            "where": location,
            "results_per_page": num_results,
            "content-type": "application/json",
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json()
                jobs = results.get("results", [])
                
                # Add icon based on job title for UI display
                for job in jobs:
                    if 'software' in job['title'].lower() or 'developer' in job['title'].lower():
                        job['icon'] = 'fas fa-laptop-code'
                    elif 'data' in job['title'].lower() or 'analyst' in job['title'].lower():
                        job['icon'] = 'fas fa-database'
                    elif 'engineer' in job['title'].lower():
                        job['icon'] = 'fas fa-cogs'
                    else:
                        job['icon'] = 'fas fa-briefcase'
            else:
                error = f"Error fetching jobs: {response.status_code}"
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    
    return render_template('jobsearch.html', jobs=jobs, error=error, back_url=url_for('dashboard'))

@app.route('/settings')
@login_required
def settings():
    """Placeholder for settings page."""
    return render_template('settings.html', back_url=url_for('dashboard'))

@app.route('/textbot')
@login_required
def textbot():
    """Textbook bot page with PDF processing and TTS."""
    return render_template('textbot.html', back_url=url_for('dashboard'))

# Create a temporary directory for audio files
TEMP_AUDIO_DIR = os.path.join(tempfile.gettempdir(), 'fc_audio_files')
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

@app.route('/upload-pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Handle PDF uploads and processing."""
    if 'pdf-file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    pdf_file = request.files['pdf-file']
    if pdf_file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'File must be a PDF'})
    
    # Save the PDF file to a temporary location for future access
    temp_dir = os.path.join(tempfile.gettempdir(), 'fc_pdf_files')
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_pdf_path = os.path.join(temp_dir, secure_filename(pdf_file.filename))
    pdf_file.save(temp_pdf_path)
    
    # Store PDF in session for later use
    if 'pdf_data' not in session:
        session['pdf_data'] = {}
    
    # Process the PDF
    page_num = int(request.form.get('page', 0))
    
    # Open the saved file for processing
    with open(temp_pdf_path, 'rb') as f:
        result = process_pdf(f, page_num)
    
    if result['success']:
        # Store basic info in session
        session['pdf_data']['filename'] = secure_filename(pdf_file.filename)
        session['pdf_data']['total_pages'] = result['total_pages']
        session['pdf_data']['current_page'] = page_num
        session['pdf_data']['temp_path'] = temp_pdf_path
        # Store the text content for summarization - combine sentences
        if 'sentences' in result:
            session['pdf_text'] = '. '.join(result['sentences'])
        else:
            session['pdf_text'] = ''
        session.modified = True
    
    return jsonify(result)

@app.route('/get-pdf-page', methods=['POST'])
@login_required
def get_pdf_page():
    """Get a specific page from the uploaded PDF."""
    if 'pdf_data' not in session or 'temp_path' not in session['pdf_data']:
        return jsonify({'success': False, 'error': 'No PDF uploaded or file not found'})
    
    page_num = int(request.form.get('page', 0))
    temp_pdf_path = session['pdf_data']['temp_path']
    
    if not os.path.exists(temp_pdf_path):
        return jsonify({'success': False, 'error': 'PDF file not found'})
    
    # Open the saved file for processing
    with open(temp_pdf_path, 'rb') as f:
        result = process_pdf(f, page_num)
    
    if result['success']:
        session['pdf_data']['current_page'] = page_num
        if 'text' in result:
            session['pdf_text'] = result['text']
        elif 'sentences' in result:
            session['pdf_text'] = '. '.join(result['sentences'])
        else:
            session['pdf_text'] = ''
        session.modified = True
    
    return jsonify(result)

@app.route('/text-to-speech', methods=['POST'])
@login_required
def generate_speech():
    """Generate speech from text."""
    text = request.form.get('text', '')
    
    if not text:
        return jsonify({'success': False, 'error': 'No text provided'})
    
    try:
        audio_file = text_to_speech(text, TEMP_AUDIO_DIR)
        filename = os.path.basename(audio_file)
        
        return jsonify({
            'success': True,
            'audio_url': url_for('serve_audio', filename=filename)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/audio/<filename>')
@login_required
def serve_audio(filename):
    """Serve generated audio files."""
    return send_file(os.path.join(TEMP_AUDIO_DIR, filename), mimetype='audio/mp3')

def extract_summarize_text(text, num_sentences=3):
    """
    Extractive summarization using NLTK.
    
    Args:
        text (str): The text to summarize
        num_sentences (int): Number of sentences to include in the summary
        
    Returns:
        str: The summarized text
    """
    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    
    # If text is too short, return the original text
    if len(sentences) <= num_sentences:
        return text
    
    # Preprocess the text
    stop_words = set(stopwords.words('english') + list(punctuation))
    words = word_tokenize(text.lower())
    
    # Remove stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    # Calculate word frequencies
    word_frequencies = FreqDist(filtered_words)
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word]
                else:
                    sentence_scores[i] += word_frequencies[word]
    
    # Get the top N sentences with highest scores
    summary_sentences_indices = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary_sentences_indices.sort()  # Sort to maintain original order
    
    # Construct the summary
    summary = ' '.join([sentences[i] for i in summary_sentences_indices])
    
    return summary

def ai_summarize_text(text, max_tokens=150):
    """
    AI-powered summarization using OpenAI API.
    
    Args:
        text (str): The text to summarize
        max_tokens (int): Maximum tokens for the summary
        
    Returns:
        str: The AI-generated summary
    """
    try:
        # If client is None, the API key wasn't available
        if client is None:
            print("OpenAI client not available, falling back to extractive summarization")
            return extract_summarize_text(text)
            
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                {"role": "user", "content": f"Please summarize the following text in about {max_tokens} tokens:\n\n{text}"}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error with AI summarization: {str(e)}")
        # Fall back to extractive summarization if AI fails
        return extract_summarize_text(text)

def search_youtube(query, max_results=6):
    """
    Searches YouTube for videos based on a query using YouTube Data API v3.

    Args:
        query (str): The search term or concept.
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries, each containing video details
              (title, video_id, channel_title), or None if an error occurs.
    """
    try:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            print("YouTube API key not found in environment variables")
            return None

        api_service_name = "youtube"
        api_version = "v3"

        # Build the YouTube service object
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=api_key,
            static_discovery=False)

        # Make the API call
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        if 'items' in response:
            for item in response['items']:
                # Extract relevant information from the response
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                channel_title = item['snippet']['channelTitle']
                
                # Extract thumbnail URLs
                thumbnails = item['snippet']['thumbnails']
                thumbnail_url = thumbnails.get('high', {}).get('url') or \
                               thumbnails.get('medium', {}).get('url') or \
                               thumbnails.get('default', {}).get('url')
                
                videos.append({
                    'title': title,
                    'video_id': video_id,
                    'channel_title': channel_title,
                    'thumbnail_url': thumbnail_url
                })
        return videos

    except googleapiclient.errors.HttpError as e:
        # Handle API errors gracefully
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        if e.resp.status == 403:
            print("This might be due to an invalid API key or exceeding quota.")
        return None
    except Exception as e:
        # Handle other potential errors
        print(f"An unexpected error occurred: {e}")
        return None

@app.route('/search-videos', methods=['POST'])
def search_videos():
    """API endpoint to search for videos based on a concept."""
    try:
        concept = request.form.get('concept', '')
        if not concept:
            return jsonify({'success': False, 'error': 'No concept provided'}), 400
            
        # Search for videos using the YouTube API
        videos = search_youtube(concept)
        
        if videos is None:
            return jsonify({'success': False, 'error': 'Failed to fetch videos. Please try again later.'}), 500
            
        return jsonify({
            'success': True,
            'videos': videos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/summarize-pdf', methods=['POST'])
def summarize_pdf():
    """API endpoint to summarize the uploaded PDF."""
    try:
        if 'pdf_text' not in session:
            return jsonify({'error': 'No PDF content available. Please upload a PDF first.'}), 400
            
        text = session['pdf_text']
        method = request.form.get('method', 'extractive')  # 'extractive' or 'ai'
        sentences = int(request.form.get('sentences', 3))
        
        if method == 'ai':
            summary = ai_summarize_text(text)
        else:
            summary = extract_summarize_text(text, sentences)
            
        return jsonify({
            'success': True,
            'summary': summary,
            'original_length': len(text),
            'summary_length': len(summary),
            'reduction_percentage': round((1 - len(summary) / len(text)) * 100, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure the database exists (run your schema script if needed)
    if not os.path.exists(app.config['DATABASE']):
        print(f"Database file '{app.config['DATABASE']}' not found.")
        print("Please run the database creation script first.")
        exit()
    app.run(debug=True) # debug=True enables auto-reloading and error pages