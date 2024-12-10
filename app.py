import os
import logging
import secrets
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate a secure secret key
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Data structures combined into a single dictionary
app_data = {
    'quiz_attempts': {},  # Format: {topic: {'attempts': int, 'scores': [float], 'max_attempts': int}}
    'quiz_data': {
        'Technology and Computer Science': {
            'questions': [
                {'text': 'What is a variable in programming?', 'options': ['A container for storing data values', 'A type of loop', 'A mathematical operation', 'A programming language'], 'correct': 0},
                {'text': 'What is object-oriented programming?', 'options': ['A way to write faster code', 'A programming paradigm based on objects containing data and code', 'A type of database', 'A programming language'], 'correct': 1}
            ],
            'passing_score': 1
        },
        'Data Science and Analytics': {
            'questions': [
                {'text': 'What is data preprocessing?', 'options': ['Analyzing data', 'Collecting data', 'Cleaning and preparing data for analysis', 'Visualizing data'], 'correct': 2},
                {'text': 'Which is NOT a common type of data visualization?', 'options': ['Bar chart', 'Pie chart', 'Line graph', 'Sound wave'], 'correct': 3}
            ],
            'passing_score': 1
        }
    },
    'recommendations': {
        'Technology and Computer Science': {
            'videos': [{'id': 'v1', 'title': 'Introduction to Programming Concepts', 'description': 'A comprehensive overview of basic programming concepts', 'duration': '45 minutes', 'url': 'https://example.com/video1', 'completed': False, 'credits_unlocked': False},
                       {'id': 'v2', 'title': 'Object-Oriented Programming Basics', 'description': 'Learn about classes, objects, and OOP principles', 'duration': '60 minutes', 'url': 'https://example.com/video2', 'completed': False, 'credits_unlocked': False}],
            'articles': [{'id': 'a1', 'title': 'Getting Started with Python', 'description': 'A beginner-friendly guide to Python programming', 'reading_time': '15 minutes', 'url': 'https://example.com/article1', 'completed': False, 'credits_unlocked': False},
                         {'id': 'a2', 'title': 'Best Practices in Software Development', 'description': 'Essential practices for writing clean, maintainable code', 'reading_time': '20 minutes', 'url': 'https://example.com/article2', 'completed': False, 'credits_unlocked': False}],
            'papers': [{'id': 'p1', 'title': 'Modern Software Development Methodologies', 'authors': 'John Doe, Jane Smith', 'abstract': 'An analysis of current software development practices', 'published_date': '2024-01-15', 'url': 'https://example.com/paper1', 'completed': False, 'credits_unlocked': False}]
        },
        'Data Science and Analytics': {
            'videos': [{'id': 'v3', 'title': 'Introduction to Data Science', 'description': 'Understanding the basics of data science', 'duration': '50 minutes', 'url': 'https://example.com/video3', 'completed': False, 'credits_unlocked': False}],
            'articles': [{'id': 'a3', 'title': 'Data Analysis Fundamentals', 'description': 'Learn the basics of data analysis', 'reading_time': '25 minutes', 'url': 'https://example.com/article3', 'completed': False, 'credits_unlocked': False}],
            'papers': [{'id': 'p2', 'title': 'Advanced Data Visualization Techniques', 'authors': 'Alice Johnson, Bob Wilson', 'abstract': 'Exploring modern data visualization methods', 'published_date': '2024-02-01', 'url': 'https://example.com/paper2', 'completed': False, 'credits_unlocked': False}]
        }
    },
    'user_materials': {},  # Format: {topic: [{'id': str, 'type': str, 'title': str, 'description': str, 'url': str, 'filename': str}]}
    'topic_details': {
        'Technology and Computer Science': {
            'title': 'Technology and Computer Science',
            'level': 'Intermediate',
            'progress': 65,
            'start_date': '2024-12-01',
            'topics': [
                {'week': 1, 'title': 'Introduction to Programming', 'status': 'Completed', 'progress': 100, 'contents': ['Basic Programming Concepts', 'Variables and Data Types', 'Control Structures', 'Functions and Methods']},
                {'week': 2, 'title': 'Object-Oriented Programming', 'status': 'In Progress', 'progress': 60, 'contents': ['Classes and Objects', 'Inheritance and Polymorphism', 'Encapsulation', 'Design Patterns']}
            ]
        },
        'Data Science and Analytics': {
            'title': 'Data Science and Analytics',
            'level': 'Beginner',
            'progress': 25,
            'start_date': '2024-11-15',
            'topics': [
                {'week': 1, 'title': 'Introduction to Data Science', 'status': 'In Progress', 'progress': 45, 'contents': ['What is Data Science?', 'Data Collection and Preprocessing', 'Exploratory Data Analysis', 'Basic Statistics']},
                {'week': 2, 'title': 'Data Visualization', 'status': 'Not Started', 'progress': 0, 'contents': ['Visualization Principles', 'Charts and Graphs', 'Interactive Visualizations', 'Storytelling with Data']}
            ]
        }
    }
}

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('user_loggedin_page'))
    return render_template('index.html')

@app.route('/user_loggedin_page')
def user_loggedin_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user_loggedin_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Mock login
        session['user_id'] = 1
        flash('Successfully logged in!', 'success')
        return redirect(url_for('user_loggedin_page'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        flash('Registration functionality will be implemented soon.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/learning-plan', methods=['GET', 'POST'])
def learning_plan():
    if request.method == 'POST':
        time.sleep(2)  # Simulate processing time
        return jsonify({'status': 'success', 'message': 'Learning plan updated'})
    
    learning_weeks = [
        {'week': 1, 'title': 'Introduction to Programming', 'description': 'Basic concepts, syntax, and fundamental programming principles', 'start_date': '2024-12-10', 'end_date': '2024-12-16'},
        {'week': 2, 'title': 'Variables and Data Types', 'description': 'Understanding different types of data and how to work with variables', 'start_date': '2024-12-17', 'end_date': '2024-12-23'}
    ]
    return render_template('learning_plan.html', learning_weeks=learning_weeks)

@app.route('/learning-history')
def learning_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    learning_history = [{'topic': 'Tech', 'progress': 65}, {'topic': 'Data Science', 'progress': 25}]
    return render_template('learning_history.html', learning_history=learning_history)

@app.route('/my-learning-details/<topic>')
def my_learning_details(topic):
    details = app_data['topic_details'].get(topic)
    if not details:
        flash('Topic not found', 'error')
        return redirect(url_for('learning_history'))
    return render_template('my_learning_details.html', details=details)

@app.route('/learning-recommendations/<topic>')
def learning_recommendations(topic):
    recommendations = app_data['recommendations'].get(topic, {'videos': [], 'articles': [], 'papers': []})
    return render_template('learning_recommendations.html', recommendations=recommendations, topic=topic)

@app.route('/quiz/<topic>/<item_id>')
def show_quiz(topic, item_id):
    if topic not in app_data['quiz_data']:
        flash('Quiz not available for this topic', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    questions = app_data['quiz_data'][topic]['questions']
    return render_template('quiz.html', topic=topic, item_id=item_id, questions=questions)

@app.route('/submit-quiz/<topic>/<item_id>', methods=['POST'])
def submit_quiz(topic, item_id):
    if topic not in app_data['quiz_data']:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404
    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/mark-recommendation/<topic>/<item_id>', methods=['POST'])
def mark_recommendation(topic, item_id):
    flash('Recommendation marked as completed!', 'success')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)