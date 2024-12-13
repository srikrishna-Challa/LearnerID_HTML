from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///learnerid.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize all data structures at the top
quiz_attempts = {}
topic_details = {
    'Technology and Computer Science': {
        'title': 'Technology and Computer Science',
        'level': 'Intermediate',
        'progress': 65,
        'status': 'In Progress',
        'total_duration': '12 weeks',
        'start_date': '2024-01-01',
        'topics': [
            {
                'title': 'Introduction to Programming',
                'week': 1,
                'status': 'Completed',
                'progress': 100
            },
            {
                'title': 'Data Structures',
                'week': 2,
                'status': 'In Progress',
                'progress': 45
            }
        ]
    },
    'Data Science': {
        'title': 'Data Science',
        'level': 'Beginner',
        'progress': 25,
        'status': 'Just Started',
        'total_duration': '8 weeks',
        'start_date': '2024-02-01',
        'topics': [
            {
                'title': 'Python Basics',
                'week': 1,
                'status': 'In Progress',
                'progress': 30
            }
        ]
    }
}

# Initialize recommendations data
recommendations_data = {
    'Technology and Computer Science': {
        'Video Resources': [
            {
                'id': 'video_1',
                'title': 'Introduction to Programming Concepts',
                'type': 'video',
                'description': 'A comprehensive overview of basic programming concepts',
                'url': 'https://example.com/intro-programming',
                'duration': '45 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'video_2',
                'title': 'Object-Oriented Programming Explained',
                'type': 'video',
                'description': 'Learn about classes, objects, and OOP principles',
                'url': 'https://example.com/oop-basics',
                'duration': '30 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Reading Materials': [
            {
                'id': 'reading_1',
                'title': 'Programming Best Practices Guide',
                'type': 'article',
                'description': 'Essential coding practices and conventions',
                'url': 'https://example.com/programming-practices',
                'reading_time': '15 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'reading_2',
                'title': 'Algorithm Design Fundamentals',
                'type': 'article',
                'description': 'Introduction to algorithm design and analysis',
                'url': 'https://example.com/algo-basics',
                'reading_time': '20 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Practice Resources': [
            {
                'id': 'practice_1',
                'title': 'Programming Exercises Collection',
                'type': 'exercise',
                'description': 'Hands-on coding exercises for practice',
                'url': 'https://example.com/programming-exercises',
                'estimated_time': '1 hour',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ]
    }
}

learning_journals = []  # Initialize empty list for learning journals
user_materials = {}  # Initialize empty dict for user materials

# Initialize quiz attempts for each topic
for course in topic_details.values():
    for topic in course['topics']:
        quiz_attempts[topic['title']] = {
            'attempts': 0,
            'scores': [],
            'max_attempts': 3
        }

quiz_data = {
    'Introduction to Programming': {
        'questions': [
            {
                'question': 'What is a variable?',
                'options': ['A container for data', 'A programming language', 'A computer', 'A website'],
                'correct': 0
            }
        ],
        'passing_score': 1
    }
}

topic_details = {
    'Technology and Computer Science': {
        'title': 'Technology and Computer Science',
        'level': 'Intermediate',
        'progress': 65,
        'status': 'In Progress',
        'total_duration': '12 weeks',
        'start_date': '2024-01-01',
        'topics': [
            {
                'title': 'Introduction to Programming',
                'week': 1,
                'status': 'Completed',
                'progress': 100
            },
            {
                'title': 'Data Structures',
                'week': 2,
                'status': 'In Progress',
                'progress': 45
            }
        ]
    }
}

recommendations_data = {
    'Technology and Computer Science': {
        'Video Resources': [
            {
                'id': 'video_1',
                'title': 'Introduction to Programming Concepts',
                'type': 'video',
                'description': 'A comprehensive overview of basic programming concepts',
                'url': 'https://example.com/intro-programming',
                'duration': '45 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'video_2',
                'title': 'Object-Oriented Programming Explained',
                'type': 'video',
                'description': 'Learn about classes, objects, and OOP principles',
                'url': 'https://example.com/oop-basics',
                'duration': '30 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Reading Materials': [
            {
                'id': 'reading_1',
                'title': 'Programming Best Practices Guide',
                'type': 'article',
                'description': 'Essential coding practices and conventions',
                'url': 'https://example.com/programming-practices',
                'reading_time': '15 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'reading_2',
                'title': 'Algorithm Design Fundamentals',
                'type': 'article',
                'description': 'Introduction to algorithm design and analysis',
                'url': 'https://example.com/algo-basics',
                'reading_time': '20 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Practice Resources': [
            {
                'id': 'practice_1',
                'title': 'Programming Exercises Collection',
                'type': 'exercise',
                'description': 'Hands-on coding exercises for practice',
                'url': 'https://example.com/programming-exercises',
                'estimated_time': '1 hour',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ]
    }
}

user_materials = {}

# Mock data for quizzes and recommendations
recommendations_data = {
    'Technology and Computer Science': {
        'Video Resources': [
            {
                'id': 'video_1',
                'title': 'Introduction to Programming Concepts',
                'type': 'video',
                'description': 'A comprehensive overview of basic programming concepts',
                'url': 'https://example.com/intro-programming',
                'duration': '45 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'video_2',
                'title': 'Object-Oriented Programming Explained',
                'type': 'video',
                'description': 'Learn about classes, objects, and OOP principles',
                'url': 'https://example.com/oop-basics',
                'duration': '30 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Reading Materials': [
            {
                'id': 'reading_1',
                'title': 'Programming Best Practices Guide',
                'type': 'article',
                'description': 'Essential coding practices and conventions',
                'url': 'https://example.com/programming-practices',
                'reading_time': '15 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'reading_2',
                'title': 'Algorithm Design Fundamentals',
                'type': 'article',
                'description': 'Introduction to algorithm design and analysis',
                'url': 'https://example.com/algo-basics',
                'reading_time': '20 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Practice Resources': [
            {
                'id': 'practice_1',
                'title': 'Programming Exercises Collection',
                'type': 'exercise',
                'description': 'Hands-on coding exercises for practice',
                'url': 'https://example.com/programming-exercises',
                'estimated_time': '1 hour',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ]
    }
}

# Mock data for quizzes and recommendations
recommendations_data = {
    'Technology and Computer Science': {
        'Video Resources': [
            {
                'id': 'video_1',
                'title': 'Introduction to Programming Concepts',
                'type': 'video',
                'description': 'A comprehensive overview of basic programming concepts',
                'url': 'https://example.com/intro-programming',
                'duration': '45 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'video_2',
                'title': 'Object-Oriented Programming Explained',
                'type': 'video',
                'description': 'Learn about classes, objects, and OOP principles',
                'url': 'https://example.com/oop-basics',
                'duration': '30 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Reading Materials': [
            {
                'id': 'reading_1',
                'title': 'Programming Best Practices Guide',
                'type': 'article',
                'description': 'Essential coding practices and conventions',
                'url': 'https://example.com/programming-practices',
                'reading_time': '15 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            },
            {
                'id': 'reading_2',
                'title': 'Algorithm Design Fundamentals',
                'type': 'article',
                'description': 'Introduction to algorithm design and analysis',
                'url': 'https://example.com/algo-basics',
                'reading_time': '20 mins',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ],
        'Practice Resources': [
            {
                'id': 'practice_1',
                'title': 'Programming Exercises Collection',
                'type': 'exercise',
                'description': 'Hands-on coding exercises for practice',
                'url': 'https://example.com/programming-exercises',
                'estimated_time': '1 hour',
                'completed': False,
                'credits_unlocked': False,
                'notes': []
            }
        ]
    }
}

# Initialize topic details
topic_details = {
    'Technology and Computer Science': {
        'title': 'Technology and Computer Science',
        'level': 'Intermediate',
        'progress': 65,
        'start_date': '2024-12-01',
        'topics': [
            {
                'title': 'Introduction to Programming',
                'week': 1,
                'status': 'Completed',
                'progress': 100
            },
            {
                'title': 'Data Structures',
                'week': 2,
                'status': 'In Progress',
                'progress': 45
            }
        ]
    }
}
user_materials = {}
# Mock data for learning topics and details
topic_details = {
    'Technology and Computer Science': {
        'title': 'Technology and Computer Science',
        'level': 'Intermediate',
        'progress': 65,
        'start_date': '2024-12-01',
        'topics': [
            {
                'title': 'Introduction to Programming',
                'week': 1,
                'status': 'Completed',
                'progress': 100
            },
            {
                'title': 'Data Structures',
                'week': 2,
                'status': 'In Progress',
                'progress': 45
            }
        ]
    },
    'Data Science and Analytics': {
        'title': 'Data Science and Analytics',
        'level': 'Beginner',
        'progress': 25,
        'start_date': '2024-11-15',
        'topics': [
            {
                'title': 'Python for Data Science',
                'week': 1,
                'status': 'In Progress',
                'progress': 30
            },
            {
                'title': 'Statistical Analysis',
                'week': 2,
                'status': 'Not Started',
                'progress': 0
            }
        ]
    }
}
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    learning_journals = db.relationship('LearningJournalEntry', backref='author', lazy=True)

class LearningJournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    note_content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def get_current_user():
    if 'user_id' in session:
        # Return a simple dictionary with user data for testing
        return {
            'id': session.get('user_id'),
            'name': session.get('user_name', 'Test User'),
            'email': session.get('user_email', 'test@example.com')
        }
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-learning-journal', methods=['GET', 'POST'])
def create_learning_journal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Create placeholder entries
    placeholder_entries = [
        {
            'id': 1,
            'title': 'Introduction to Python Programming',
            'description': 'Learning the basics of Python programming language',
            'created_at': datetime.now()
        },
        {
            'id': 2,
            'title': 'Web Development Fundamentals',
            'description': 'Understanding HTML, CSS, and JavaScript basics',
            'created_at': datetime.now()
        },
        {
            'id': 3,
            'title': 'Data Structures and Algorithms',
            'description': 'Exploring fundamental computer science concepts',
            'created_at': datetime.now()
        }
    ]
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title:
            new_entry = {
                'id': len(placeholder_entries) + 1,
                'title': title,
                'description': description,
                'created_at': datetime.now()
            }
            placeholder_entries.append(new_entry)
            return redirect(url_for('learning_journal_details', entry_id=new_entry['id']))
                
    return render_template('learning_journal.html', entries=placeholder_entries, user=get_current_user())

@app.route('/learning-journal/<int:entry_id>', methods=['GET', 'POST'])
def learning_journal_details(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Create a placeholder entry for demonstration
    entry = {
        'id': entry_id,
        'title': 'Introduction to Python Programming' if entry_id == 1 else 'Web Development Fundamentals',
        'description': 'Learning the basics of Python programming language' if entry_id == 1 else 'Understanding HTML, CSS, and JavaScript basics',
        'notes': '',
        'created_at': datetime.now()
    }
    
    if request.method == 'POST':
        new_notes = request.form.get('additional_notes')
        if new_notes:
            current_notes = entry['notes'] if entry['notes'] else ''
            entry['notes'] = current_notes + '\n\n' + new_notes
    
    return render_template('learning_journal_details.html', entry=entry, user=get_current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        # Create a mock user for testing
        mock_user = User()
        mock_user.id = 1
        mock_user.name = "Test User"
        mock_user.email = email
        
        # Log in the mock user
        login_user(mock_user)
        return redirect(url_for('user_loggedin_page'))
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('user_loggedin_page'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user-loggedin')
def user_loggedin_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user_loggedin_page.html', user=get_current_user())

@app.route('/mails')
def mails():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('mails.html')

@app.route('/learning-credits')
def learning_credits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('learning_credits.html')


@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('index.html')



@app.route('/learning-paths')
def learning_paths():
    return render_template('learning_paths.html')

@app.route('/add-to-learning-goals', methods=['POST'])
def add_to_learning_goals():
    topics = request.json.get('topics', [])
    if not topics:
        return jsonify({'status': 'error', 'message': 'No topics selected'}), 400
    
    # Add selected topics to learning history
    for topic_title in topics:
        if topic_title not in topic_details:
            topic_details[topic_title] = {
                'title': topic_title,
                'level': 'Beginner',
                'progress': 0,
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'topics': []
            }
    
    flash(f'Added {len(topics)} topics to your learning goals!', 'success')
    return jsonify({'status': 'success'})

@app.route('/learning-plan', methods=['GET', 'POST'])
def learning_plan():
    if request.method == 'POST':
        # Process the learning preferences
        preferences = request.get_json()
        flash('Your learning plan has been updated successfully!', 'success')
        return jsonify({'status': 'success', 'message': 'Learning plan updated'})

    # Sample learning topics
    learning_topics = [
        {
            'title': 'Introduction to Programming',
            'description': 'Learn the fundamentals of programming including basic concepts, syntax, and problem-solving approaches',
            'time_required': '20',
            'objectives': [
                'Understand basic programming concepts and terminology',
                'Learn about variables, data types, and operators',
                'Master control structures (if/else, loops)',
                'Write basic functions and understand scope'
            ]
        },
        {
            'title': 'Web Development Fundamentals',
            'description': 'Explore the core technologies that power the modern web including HTML, CSS, and JavaScript',
            'time_required': '25',
            'objectives': [
                'Build responsive web pages using HTML and CSS',
                'Understand DOM manipulation with JavaScript',
                'Learn about web accessibility principles',
                'Practice modern web development workflows'
            ]
        },
        {
            'title': 'Data Science Essentials',
            'description': 'Get started with data analysis and visualization using Python and popular data science libraries',
            'time_required': '30',
            'objectives': [
                'Learn data manipulation with pandas',
                'Create insightful visualizations',
                'Perform basic statistical analysis',
                'Work with real-world datasets'
            ]
        }
    ]
    
    return render_template('learning_plan.html', learning_topics=learning_topics)

@app.route('/my-learning-details/<topic>')
def my_learning_details(topic):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    details = topic_details.get(topic)
    if not details:
        flash('Topic not found', 'error')
        return redirect(url_for('learning_history'))
    
    return render_template('my_learning_details.html', 
                         details=details,
                         user=get_current_user())

@app.route('/learning-recommendations/<topic>')
def learning_recommendations(topic):
    app.logger.debug(f"Accessing recommendations for topic: {topic}")
    
    # Get the parent course and week information
    parent_course = None
    week_number = None
    topic_info = None
    
    for course, details in topic_details.items():
        for week_topic in details['topics']:
            if week_topic['title'] == topic:
                parent_course = course
                week_number = week_topic['week']
                topic_info = week_topic
                break
        if parent_course:
            break
    
    # Initialize quiz attempts if not exists
    if topic not in quiz_attempts:
        quiz_attempts[topic] = {'attempts': 0, 'scores': [], 'max_attempts': 3}
    
    # Get recommendations for the exact topic name
    recommendations = recommendations_data.get(parent_course, {})
    video_resources = recommendations.get('Video Resources', [])
    reading_materials = recommendations.get('Reading Materials', [])
    topic_materials = user_materials.get(topic, [])
    
    # Calculate quiz statistics
    topic_attempts = quiz_attempts.get(topic, {})
    quiz_stats = {
        'attempts_made': topic_attempts.get('attempts', 0),
        'avg_score': sum(topic_attempts.get('scores', [])) / len(topic_attempts.get('scores', [1])) if topic_attempts.get('scores') else 0,
        'attempts_left': topic_attempts.get('max_attempts', 3) - topic_attempts.get('attempts', 0)
    }
    
    progress = topic_info.get('progress', 0) if topic_info else 0
    
    return render_template('learning_recommendations.html', 
                         video_resources=video_resources,
                         reading_materials=reading_materials,
                         topic=topic,
                         parent_course=parent_course,
                         week_number=week_number,
                         topic_info=topic_info,
                         progress=progress,
                         quiz_stats=quiz_stats,
                         user_materials=topic_materials)

@app.route('/topic-quiz/<topic>')
def show_topic_quiz(topic):
    if topic not in quiz_data:
        flash('Quiz not available for this topic', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    # Initialize attempts tracking if not exists
    if topic not in quiz_attempts:
        quiz_attempts[topic] = {
            'attempts': 0,
            'scores': [],
            'max_attempts': 3
        }
    
    attempts_info = quiz_attempts[topic]
    avg_score = sum(attempts_info['scores']) / len(attempts_info['scores']) if attempts_info['scores'] else 0
    attempts_left = attempts_info['max_attempts'] - attempts_info['attempts']
    
    questions = quiz_data[topic]['questions']
    return render_template('quiz.html', 
                         topic=topic,
                         item_id=None,  # This indicates it's a topic-level quiz
                         questions=questions,
                         attempts=attempts_info['attempts'],
                         avg_score=round(avg_score, 2),
                         attempts_left=attempts_left)

@app.route('/quiz/<topic>/<item_id>')
def show_quiz(topic, item_id):
    if topic not in quiz_data:
        flash('Quiz not available for this topic', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    # Initialize attempts tracking if not exists
    if topic not in quiz_attempts:
        quiz_attempts[topic] = {
            'attempts': 0,
            'scores': [],
            'max_attempts': 3
        }
    
    attempts_info = quiz_attempts[topic]
    if attempts_info['attempts'] >= attempts_info['max_attempts']:
        flash('You have reached the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    questions = quiz_data[topic]['questions']
    avg_score = sum(attempts_info['scores']) / len(attempts_info['scores']) if attempts_info['scores'] else 0
    attempts_left = attempts_info['max_attempts'] - attempts_info['attempts']
    
    return render_template('quiz.html', 
                         topic=topic,
                         item_id=item_id,
                         questions=questions,
                         attempts=attempts_info['attempts'],
                         avg_score=round(avg_score, 2),
                         attempts_left=attempts_left)

@app.route('/submit-topic-quiz/<topic>', methods=['POST'])
def submit_topic_quiz(topic):
    if topic not in quiz_data:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404
    
    # Check if maximum attempts reached
    if quiz_attempts[topic]['attempts'] >= quiz_attempts[topic]['max_attempts']:
        flash('You have reached the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    questions = quiz_data[topic]['questions']
    correct_count = 0
    
    # Grade the quiz
    for i in range(len(questions)):
        user_answer = request.form.get(f'q{i+1}')
        if user_answer and int(user_answer) == questions[i]['correct']:
            correct_count += 1
    
    # Calculate score as percentage
    score = (correct_count / len(questions)) * 100
    
    # Update attempts tracking
    quiz_attempts[topic]['attempts'] += 1
    quiz_attempts[topic]['scores'].append(score)
    
    # Check if passed
    passed = correct_count >= quiz_data[topic]['passing_score']
    
    if passed:
        # Update topic completion status
        for course in topic_details.values():
            for week_topic in course['topics']:
                if week_topic['title'] == topic:
                    week_topic['status'] = 'Completed'
                    week_topic['progress'] = 100
                    break
        
        flash(f'Congratulations! You passed the quiz with {correct_count} correct answers. Topic marked as completed!', 'success')
    else:
        attempts_left = quiz_attempts[topic]['max_attempts'] - quiz_attempts[topic]['attempts']
        flash(f'You got {correct_count} answers correct. You need {quiz_data[topic]["passing_score"]} to pass. You have {attempts_left} attempts left!', 'error')
    
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/submit-quiz/<topic>/<item_id>', methods=['POST'])
def submit_quiz(topic, item_id):
    if topic not in quiz_data:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404
    
    # Check if maximum attempts reached
    if quiz_attempts[topic]['attempts'] >= quiz_attempts[topic]['max_attempts']:
        flash('You have reached the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    questions = quiz_data[topic]['questions']
    correct_count = 0
    
    # Grade the quiz
    for i in range(len(questions)):
        user_answer = request.form.get(f'q{i+1}')
        if user_answer and int(user_answer) == questions[i]['correct']:
            correct_count += 1
    
    # Calculate score as percentage
    score = (correct_count / len(questions)) * 100
    
    # Update attempts tracking
    quiz_attempts[topic]['attempts'] += 1
    quiz_attempts[topic]['scores'].append(score)
    
    # Check if passed
    passed = correct_count >= quiz_data[topic]['passing_score']
    
    if passed:
        # Find and update the item's credits status
        for section in recommendations_data[topic].values():
            for item in section:
                if item['id'] == item_id:
                    item['credits_unlocked'] = True
        
        flash(f'Congratulations! You passed the quiz with {correct_count} correct answers. Learning credits have been unlocked!', 'success')
    else:
        attempts_left = quiz_attempts[topic]['max_attempts'] - quiz_attempts[topic]['attempts']
        flash(f'You got {correct_count} answers correct. You need {quiz_data[topic]["passing_score"]} to pass. You have {attempts_left} attempts left!', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/weekly-reading-details/<week_start>')
def weekly_reading_details(week_start):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Mock weekly readings data (replace with database query in production)
    weekly_readings = [
        {
            'start_date': '2024-12-09',
            'end_date': '2024-12-15',
            'total_readings': 8,
            'total_duration': '4 hours',
            'topics': ['Python', 'Web Development', 'Data Science'],
            'readings': [
                {
                    'title': 'Introduction to Flask',
                    'summary': 'Learn the basics of Flask web framework including routing, templates, and database integration.',
                    'date': '2024-12-09',
                    'duration': '45 minutes',
                    'topic': 'Python',
                    'tags': ['Web Development', 'Backend'],
                    'notes': 'Key concepts: Routes, Templates, Jinja2, SQLAlchemy'
                },
                {
                    'title': 'Database Design Patterns',
                    'summary': 'Understanding common database design patterns and their implementation in real-world applications.',
                    'date': '2024-12-10',
                    'duration': '60 minutes',
                    'topic': 'Database',
                    'tags': ['SQL', 'Architecture'],
                    'notes': 'Covered: Normalization, Indexing, Relationships'
                },
                {
                    'title': 'RESTful API Design',
                    'summary': 'Best practices for designing REST APIs with proper endpoint structure and response formats.',
                    'date': '2024-12-11',
                    'duration': '30 minutes',
                    'topic': 'API',
                    'tags': ['REST', 'HTTP'],
                    'notes': 'Focus on: Status codes, Authentication, Versioning'
                }
            ]
        }
    ]
    
    # Find the specific week's readings
    week_data = None
    for week in weekly_readings:
        if week['start_date'] == week_start:
            week_data = week
            break
    
    if not week_data:
        flash('Week not found', 'error')
        return redirect(url_for('learning_history'))
    
    return render_template('weekly_reading_details.html', 
                         week=week_data,
                         user=get_current_user())
@app.route('/all-reading-history')
def all_reading_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all weekly readings without the 5-item limit
    weekly_readings = [
        {
            'start_date': '2024-12-09',
            'end_date': '2024-12-15',
            'total_readings': 8,
            'total_duration': '4 hours',
            'topics': ['Python', 'Web Development', 'Data Science'],
            'readings': [
                {
                    'title': 'Introduction to Flask',
                    'summary': 'Learn the basics of Flask web framework...'
                },
                {
                    'title': 'Database Design Patterns',
                    'summary': 'Understanding common database design patterns...'
                },
                {
                    'title': 'RESTful API Design',
                    'summary': 'Best practices for designing REST APIs...'
                }
            ]
        },
        {
            'start_date': '2024-12-02',
            'end_date': '2024-12-08',
            'total_readings': 6,
            'total_duration': '3 hours',
            'topics': ['JavaScript', 'React', 'Node.js'],
            'readings': [
                {
                    'title': 'Modern JavaScript Features',
                    'summary': 'Exploring ES6+ features and their applications...'
                },
                {
                    'title': 'React Hooks Deep Dive',
                    'summary': 'Understanding React hooks and state management...'
                }
            ]
        }
    ]
    
    return render_template('all_reading_history.html', 
                         weekly_readings=weekly_readings,
                         user=get_current_user())
    
    return redirect(url_for('learning_recommendations', topic=topic))


@app.route('/add-learning-material/<topic>', methods=['POST'])
def add_learning_material(topic):
    app.logger.debug(f"Adding learning material for topic: {topic}")
    app.logger.debug(f"Form data: {request.form}")
    app.logger.debug(f"Files: {request.files}")
    
    if topic not in user_materials:
        user_materials[topic] = []
    
    material_type = request.form.get('material_type')
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    if not all([material_type, title]):
        flash('Title and material type are required', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    material_id = f"user_material_{len(user_materials[topic])}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    material = {
        'id': material_id,
        'title': title,
        'description': description,
        'type': material_type,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if material_type == 'document':
        if 'document' not in request.files:
            app.logger.error("No document file in request.files")
            flash('No file uploaded', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        file = request.files['document']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(f"{material_id}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                app.logger.debug(f"File saved successfully at: {file_path}")
                material['filename'] = filename
            except Exception as e:
                app.logger.error(f"Error saving file: {str(e)}")
                flash('Error uploading file', 'error')
                return redirect(url_for('learning_recommendations', topic=topic))
        else:
            flash('Invalid file type. Please upload PDF or Word documents.', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
    else:
        url = request.form.get('url')
        if not url:
            flash('URL is required for video/article materials', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        material['url'] = url
    
    user_materials[topic].append(material)
    flash('Learning material added successfully!', 'success')
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/download-material/<material_id>')
def download_material(material_id):
    for materials in user_materials.values():
        for material in materials:
            if material['id'] == material_id and material['type'] == 'document':
                try:
                    return send_from_directory(
                        app.config['UPLOAD_FOLDER'],
                        material['filename'],
                        as_attachment=True
                    )
                except Exception as e:
                    app.logger.error(f"Error downloading material: {str(e)}")
                    flash('Error downloading material', 'error')
                    return redirect(request.referrer)
    
    flash('Material not found', 'error')
    return redirect(request.referrer)

@app.route('/get-notes/<resource_id>')
def get_notes(resource_id):
    note = UserNote.query.filter_by(
        user_id=1,  # Mock user_id until authentication is implemented
        resource_id=resource_id
    ).order_by(UserNote.created_at.desc()).first()
    
    if note:
        return jsonify({
            'status': 'success',
            'note': {
                'content': note.note_content,
                'summary': note.summary
            }
        })
    return jsonify({
        'status': 'success',
        'note': {
            'content': '',
            'summary': None
        }
    })

@app.route('/add-note/<topic>/<resource_id>', methods=['POST'])
def add_note(topic, resource_id):
    note_content = request.form.get('note_content')
    resource_type = request.form.get('resource_type')
    
    if not note_content:
        flash('Note content is required', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    note = UserNote(
        user_id=1,  # Mock user_id until authentication is implemented
        resource_id=resource_id,
        resource_type=resource_type,
        note_content=note_content
    )
    
    try:
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding note: {str(e)}")
        flash('Error adding note', 'error')
    
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/update-note/<note_id>', methods=['POST'])
def update_note(note_id):
    note = UserNote.query.get_or_404(note_id)
    note_content = request.form.get('note_content')
    
    if not note_content:
        return jsonify({'status': 'error', 'message': 'Note content is required'}), 400
    
    try:
        note.note_content = note_content
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Note updated successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating note: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error updating note'}), 500

@app.route('/generate-summary/<resource_id>', methods=['POST'])
def generate_summary(resource_id):
    note = UserNote.query.get_or_404(resource_id)
    
    try:
        # Mock summary generation for now
        # TODO: Integrate with OpenAI or similar API for actual summary generation
        summary = f"Summary of: {note.note_content[:100]}..."
        
        note.summary = summary
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'summary': summary
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error generating summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error generating summary'
        }), 500

@app.route('/delete-material/<material_id>', methods=['POST'])
def delete_material(material_id):
    for topic, materials in user_materials.items():
        for i, material in enumerate(materials):
            if material['id'] == material_id:
                if material['type'] == 'document':
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], material['filename']))
                    except:
                        pass
                materials.pop(i)
                flash('Material deleted successfully!', 'success')
                return redirect(url_for('learning_recommendations', topic=topic))
    
    flash('Material not found', 'error')
    return redirect(request.referrer)

@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Mock email data for demonstration
    emails = [
        {
            'subject': 'Welcome to LearnerID!',
            'sender': 'support@learnerid.com',
            'preview': 'Welcome to your personalized learning journey. Get started by exploring our courses...',
            'date': '2024-12-11',
            'unread': True
        },
        {
            'subject': 'Course Recommendation: Advanced Python',
            'sender': 'recommendations@learnerid.com',
            'preview': 'Based on your learning progress, we think you might enjoy our Advanced Python course...',
            'date': '2024-12-10',
            'unread': False
        },
        {
            'subject': 'Learning Milestone Achieved!',
            'sender': 'achievements@learnerid.com',
            'preview': "Congratulations! You've completed your first course milestone...",
            'date': '2024-12-09',
            'unread': False
        }
    ]

    return render_template('inbox.html', emails=emails)


@app.route('/mark-resource-completed/<topic>/<resource_id>', methods=['POST'])
def mark_resource_completed(topic, resource_id):
    app.logger.debug(f"Marking resource {resource_id} as completed for topic: {topic}")
    
    # Find and mark the resource as completed
    resource_found = False
    for section in recommendations_data.get(topic, {}).values():
        for item in section:
            if item['id'] == resource_id:
                item['completed'] = True
                resource_found = True
                break
        if resource_found:
            break
    
    if resource_found:
        flash('Resource has been marked as completed!', 'success')
        return jsonify({
            'status': 'success',
            'message': 'Resource marked as completed'
        })
    else:
        flash('Resource not found', 'error')
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404
@app.route('/mark-topic-completed/<topic>', methods=['POST'])
def mark_topic_completed(topic):
    app.logger.debug(f"Marking topic as completed: {topic}")
    
    # Find and update the topic status
    topic_found = False
    for course in topic_details.values():
        for week_topic in course['topics']:
            if week_topic['title'] == topic:
                week_topic['status'] = 'Completed'
                week_topic['progress'] = 100
                topic_found = True
                break
    
    if topic_found:
        flash('Topic has been marked as completed successfully!', 'success')
        return jsonify({
            'status': 'success',
            'message': 'Topic marked as completed'
        })
    else:
        flash('Topic not found', 'error')
        return jsonify({
            'status': 'error',
            'message': 'Topic not found'
        }), 404

@app.route('/learning-history')
def learning_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Mock data for learning history and progress
    learning_history = [
        {
            'topic': 'Technology and Computer Science',
            'level': 'Intermediate',
            'total_duration': '8 weeks',
            'progress': 65,
            'start_date': '2024-12-01',
            'status': 'In Progress'
        },
        {
            'topic': 'Data Science and Analytics',
            'level': 'Beginner',
            'total_duration': '12 weeks',
            'progress': 25,
            'start_date': '2024-11-15',
            'status': 'In Progress'
        },
        {
            'topic': 'Web Development Fundamentals',
            'level': 'Intermediate',
            'total_duration': '10 weeks',
            'progress': 100,
            'start_date': '2024-10-01',
            'completion_date': '2024-12-10',
            'status': 'Completed',
            'achievements': ['Full Stack Developer', 'Code Quality Expert']
        },
        {
            'topic': 'Python Programming',
            'level': 'Advanced',
            'total_duration': '6 weeks',
            'progress': 100,
            'start_date': '2024-09-15',
            'completion_date': '2024-10-30',
            'status': 'Completed',
            'achievements': ['Python Master', 'Algorithm Specialist']
        }
    ]

    # Mock recent activity data
    recent_activities = [
        {
            'type': 'completion',
            'icon': 'book-open',
            'text': 'Completed Module: Introduction to Programming',
            'time': '2 hours ago'
        },
        {
            'type': 'achievement',
            'icon': 'trophy',
            'text': 'Earned Badge: Python Basics',
            'time': 'Yesterday'
        },
        {
            'type': 'course',
            'icon': 'tasks',
            'text': 'Started New Course: Data Structures',
            'time': '2 days ago'
        }
    ]

    # Mock progress statistics
    progress_stats = {
        'current_progress': 65,
        'current_course': 'Technology and Computer Science',
        'learning_credits': 750,
        'active_courses': 2
    }

    # Mock weekly readings data
    weekly_readings = [
        {
            'start_date': '2024-12-09',
            'end_date': '2024-12-15',
            'total_readings': 8,
            'total_duration': '4 hours',
            'topics': ['Python', 'Web Development', 'Data Science'],
            'readings': [
                {
                    'title': 'Introduction to Flask',
                    'summary': 'Learn the basics of Flask web framework...'
                },
                {
                    'title': 'Database Design Patterns',
                    'summary': 'Understanding common database design patterns...'
                },
                {
                    'title': 'RESTful API Design',
                    'summary': 'Best practices for designing REST APIs...'
                }
            ]
        },
        {
            'start_date': '2024-12-02',
            'end_date': '2024-12-08',
            'total_readings': 6,
            'total_duration': '3 hours',
            'topics': ['JavaScript', 'React', 'Node.js'],
            'readings': [
                {
                    'title': 'Modern JavaScript Features',
                    'summary': 'Exploring ES6+ features and their applications...'
                },
                {
                    'title': 'React Hooks Deep Dive',
                    'summary': 'Understanding React hooks and state management...'
                }
            ]
        }
    ]

    return render_template('learning_history.html', 
                         learning_history=learning_history,
                         recent_activities=recent_activities,
                         progress_stats=progress_stats,
                         weekly_readings=weekly_readings,
                         user=get_current_user())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)