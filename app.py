from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
logging.basicConfig(level=logging.DEBUG)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///learning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Models
class UserNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)  # We'll link this to users once auth is implemented
    resource_id = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(20), nullable=False)  # 'video', 'article', or 'paper'
    note_content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class LearningJournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)  # We'll link this to users once auth is implemented
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# Create tables
with app.app_context():
    db.create_all()

# Initialize data structures
user_materials = {}
quiz_attempts = {}
recommendations_data = {
    'Technology and Computer Science': {
        'videos': [
            {
                'id': 'v1',
                'title': 'Introduction to Variables',
                'description': 'Learn about variables and data types',
                'duration': '10 mins',
                'url': 'https://example.com/video1',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a1',
                'title': 'Programming Fundamentals',
                'description': 'Basic concepts in programming',
                'reading_time': '5 mins',
                'url': 'https://example.com/article1',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p1',
                'title': 'Understanding Algorithms',
                'authors': 'John Doe, Jane Smith',
                'abstract': 'A comprehensive look at algorithmic thinking',
                'published_date': '2024-01-15',
                'url': 'https://example.com/paper1',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    }
}

topic_details = {
    'Technology and Computer Science': {
        'topics': [
            {
                'title': 'Introduction to Programming',
                'week': 1,
                'status': 'In Progress',
                'progress': 30
            }
        ]
    }
}

quiz_data = {
    'Introduction to Programming': {
        'questions': [
            {
                'text': 'What is a variable?',
                'options': [
                    'A container for storing data values',
                    'A mathematical equation',
                    'A programming language',
                    'A type of computer'
                ],
                'correct': 0
            },
            {
                'text': 'Which of these is a loop structure?',
                'options': [
                    'if-else',
                    'try-catch',
                    'for',
                    'switch'
                ],
                'correct': 2
            }
        ],
        'passing_score': 1
    }
}


# Routes
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

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('index.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Mock login for demonstration
        session['user_id'] = 1  # Mock user ID
        flash('Successfully logged in!', 'success')
        return redirect(url_for('user_loggedin_page'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        
        # TODO: Add user registration logic
        flash('Registration functionality will be implemented soon.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

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
    details = topic_details.get(topic)
    if not details:
        flash('Topic not found', 'error')
        return redirect(url_for('learning_history'))
    
    # Initialize quiz attempts for all topics if not exists
    for week_topic in details['topics']:
        topic_name = week_topic['title']
        if topic_name not in quiz_attempts:
            quiz_attempts[topic_name] = {
                'attempts': 0,
                'scores': [],
                'max_attempts': 3
            }
    
    return render_template('my_learning_details.html', 
                         details=details,
                         quiz_attempts=quiz_attempts)

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
    topic_materials = user_materials.get(topic, [])
    
    # Calculate quiz statistics
    topic_attempts = quiz_attempts.get(topic, {})
    quiz_stats = {
        'attempts_made': topic_attempts.get('attempts', 0),
        'avg_score': sum(topic_attempts.get('scores', [])) / len(topic_attempts.get('scores', [1])) if topic_attempts.get('scores') else 0,
        'attempts_left': topic_attempts.get('max_attempts', 3) - topic_attempts.get('attempts', 0)
    }
    
    return render_template('learning_recommendations.html', 
                         recommendations=recommendations,
                         topic=topic,
                         parent_course=parent_course,
                         week_number=week_number,
                         topic_info=topic_info,
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

    return redirect(request.referrer)

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

    return render_template('learning_history.html', 
                         learning_history=learning_history,
                         recent_activities=recent_activities,
                         progress_stats=progress_stats)

@app.route('/learning-journal', methods=['GET', 'POST'])
def create_learning_journal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        
        if not title or not content:
            flash('Title and content are required', 'error')
            return redirect(url_for('create_learning_journal'))
        
        entry = LearningJournalEntry(
            user_id=session['user_id'],
            title=title,
            content=content,
            category=category
        )
        
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Journal entry added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding journal entry: {str(e)}")
            flash('Error adding journal entry', 'error')
        
        return redirect(url_for('create_learning_journal'))
    
    # Get existing entries for the user, sorted by created_at (newest first)
    entries = LearningJournalEntry.query.filter_by(
        user_id=session['user_id']
    ).order_by(LearningJournalEntry.created_at.desc()).all()
    
    return render_template('learning_journal.html', entries=entries)
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

    return render_template('learning_history.html', 
                         learning_history=learning_history,
                         recent_activities=recent_activities,
                         progress_stats=progress_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)