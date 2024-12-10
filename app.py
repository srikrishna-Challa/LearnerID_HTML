from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock quiz attempts storage
quiz_attempts = {}  # Format: {topic: {'attempts': int, 'scores': [float], 'max_attempts': int}}

# Mock quiz data storage
quiz_data = {
    'Technology and Computer Science': {
        'questions': [
            {
                'text': 'What is a variable in programming?',
                'options': [
                    'A container for storing data values',
                    'A type of loop',
                    'A mathematical operation',
                    'A programming language'
                ],
                'correct': 0
            },
            {
                'text': 'What is object-oriented programming?',
                'options': [
                    'A way to write faster code',
                    'A programming paradigm based on objects containing data and code',
                    'A type of database',
                    'A programming language'
                ],
                'correct': 1
            }
        ],
        'passing_score': 1
    },
    'Data Science and Analytics': {
        'questions': [
            {
                'text': 'What is data preprocessing?',
                'options': [
                    'Analyzing data',
                    'Collecting data',
                    'Cleaning and preparing data for analysis',
                    'Visualizing data'
                ],
                'correct': 2
            },
            {
                'text': 'Which is NOT a common type of data visualization?',
                'options': [
                    'Bar chart',
                    'Pie chart',
                    'Line graph',
                    'Sound wave'
                ],
                'correct': 3
            }
        ],
        'passing_score': 1
    }
}

# Mock recommendations data storage
recommendations_data = {
    'Technology and Computer Science': {
        'videos': [
            {
                'id': 'v1',
                'title': 'Introduction to Programming Concepts',
                'description': 'A comprehensive overview of basic programming concepts',
                'duration': '45 minutes',
                'url': 'https://example.com/video1',
                'completed': False,
                'credits_unlocked': False
            },
            {
                'id': 'v2',
                'title': 'Object-Oriented Programming Basics',
                'description': 'Learn about classes, objects, and OOP principles',
                'duration': '60 minutes',
                'url': 'https://example.com/video2',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a1',
                'title': 'Getting Started with Python',
                'description': 'A beginner-friendly guide to Python programming',
                'reading_time': '15 minutes',
                'url': 'https://example.com/article1',
                'completed': False,
                'credits_unlocked': False
            },
            {
                'id': 'a2',
                'title': 'Best Practices in Software Development',
                'description': 'Essential practices for writing clean, maintainable code',
                'reading_time': '20 minutes',
                'url': 'https://example.com/article2',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p1',
                'title': 'Modern Software Development Methodologies',
                'authors': 'John Doe, Jane Smith',
                'abstract': 'An analysis of current software development practices',
                'published_date': '2024-01-15',
                'url': 'https://example.com/paper1',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    },
    'Data Science and Analytics': {
        'videos': [
            {
                'id': 'v3',
                'title': 'Introduction to Data Science',
                'description': 'Understanding the basics of data science',
                'duration': '50 minutes',
                'url': 'https://example.com/video3',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a3',
                'title': 'Data Analysis Fundamentals',
                'description': 'Learn the basics of data analysis',
                'reading_time': '25 minutes',
                'url': 'https://example.com/article3',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p2',
                'title': 'Advanced Data Visualization Techniques',
                'authors': 'Alice Johnson, Bob Wilson',
                'abstract': 'Exploring modern data visualization methods',
                'published_date': '2024-02-01',
                'url': 'https://example.com/paper2',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    }
}

# Mock user materials storage
user_materials = {}  # Format: {topic: [{'id': str, 'type': str, 'title': str, 'description': str, 'url': str, 'filename': str}]}

# Mock topic details storage
topic_details = {
    'Technology and Computer Science': {
        'title': 'Technology and Computer Science',
        'level': 'Intermediate',
        'progress': 65,
        'start_date': '2024-12-01',
        'topics': [
            {
                'week': 1,
                'title': 'Introduction to Programming',
                'status': 'Completed',
                'progress': 100,
                'contents': [
                    'Basic Programming Concepts',
                    'Variables and Data Types',
                    'Control Structures',
                    'Functions and Methods'
                ]
            },
            {
                'week': 2,
                'title': 'Object-Oriented Programming',
                'status': 'In Progress',
                'progress': 60,
                'contents': [
                    'Classes and Objects',
                    'Inheritance and Polymorphism',
                    'Encapsulation',
                    'Design Patterns'
                ]
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
                'week': 1,
                'title': 'Introduction to Data Science',
                'status': 'In Progress',
                'progress': 45,
                'contents': [
                    'What is Data Science?',
                    'Data Collection and Preprocessing',
                    'Exploratory Data Analysis',
                    'Basic Statistics'
                ]
            },
            {
                'week': 2,
                'title': 'Data Visualization',
                'status': 'Not Started',
                'progress': 0,
                'contents': [
                    'Visualization Principles',
                    'Charts and Graphs',
                    'Interactive Visualizations',
                    'Storytelling with Data'
                ]
            }
        ]
    }
}

# Mock quiz data storage
quiz_data = {
    'Technology and Computer Science': {
        'questions': [
            {
                'text': 'What is a variable in programming?',
                'options': [
                    'A container for storing data values',
                    'A type of loop',
                    'A mathematical operation',
                    'A programming language'
                ],
                'correct': 0
            },
            {
                'text': 'What is object-oriented programming?',
                'options': [
                    'A way to write faster code',
                    'A programming paradigm based on objects containing data and code',
                    'A type of database',
                    'A programming language'
                ],
                'correct': 1
            }
        ],
        'passing_score': 1
    },
    'Data Science and Analytics': {
        'questions': [
            {
                'text': 'What is data preprocessing?',
                'options': [
                    'Analyzing data',
                    'Collecting data',
                    'Cleaning and preparing data for analysis',
                    'Visualizing data'
                ],
                'correct': 2
            },
            {
                'text': 'Which is NOT a common type of data visualization?',
                'options': [
                    'Bar chart',
                    'Pie chart',
                    'Line graph',
                    'Sound wave'
                ],
                'correct': 3
            }
        ],
        'passing_score': 1
    }
}

# Mock recommendations data storage
recommendations_data = {
    'Technology and Computer Science': {
        'videos': [
            {
                'id': 'v1',
                'title': 'Introduction to Programming Concepts',
                'description': 'A comprehensive overview of basic programming concepts',
                'duration': '45 minutes',
                'url': 'https://example.com/video1',
                'completed': False,
                'credits_unlocked': False
            },
            {
                'id': 'v2',
                'title': 'Object-Oriented Programming Basics',
                'description': 'Learn about classes, objects, and OOP principles',
                'duration': '60 minutes',
                'url': 'https://example.com/video2',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a1',
                'title': 'Getting Started with Python',
                'description': 'A beginner-friendly guide to Python programming',
                'reading_time': '15 minutes',
                'url': 'https://example.com/article1',
                'completed': False,
                'credits_unlocked': False
            },
            {
                'id': 'a2',
                'title': 'Best Practices in Software Development',
                'description': 'Essential practices for writing clean, maintainable code',
                'reading_time': '20 minutes',
                'url': 'https://example.com/article2',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p1',
                'title': 'Modern Software Development Methodologies',
                'authors': 'John Doe, Jane Smith',
                'abstract': 'An analysis of current software development practices',
                'published_date': '2024-01-15',
                'url': 'https://example.com/paper1',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    },
    'Data Science and Analytics': {
        'videos': [
            {
                'id': 'v3',
                'title': 'Introduction to Data Science',
                'description': 'Understanding the basics of data science',
                'duration': '50 minutes',
                'url': 'https://example.com/video3',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a3',
                'title': 'Data Analysis Fundamentals',
                'description': 'Learn the basics of data analysis',
                'reading_time': '25 minutes',
                'url': 'https://example.com/article3',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p2',
                'title': 'Advanced Data Visualization Techniques',
                'authors': 'Alice Johnson, Bob Wilson',
                'abstract': 'Exploring modern data visualization methods',
                'published_date': '2024-02-01',
                'url': 'https://example.com/paper2',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    }
}

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
    avg_score = sum(attempts_info['scores']) / len(attempts_info['scores']) if attempts_info['scores'] else 0
    attempts_left = attempts_info['max_attempts'] - attempts_info['attempts']
    
    questions = quiz_data[topic]['questions']
    return render_template('quiz.html', 
                         topic=topic, 
                         item_id=item_id, 
                         questions=questions,
                         attempts=attempts_info['attempts'],
                         avg_score=round(avg_score, 2),
                         attempts_left=attempts_left)

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

@app.route('/learning-plan', methods=['GET', 'POST'])
def learning_plan():
    if request.method == 'POST':
        # Simulate AI processing time
        import time
        time.sleep(2)
        flash('Your learning plan has been updated successfully!', 'success')
        return jsonify({'status': 'success', 'message': 'Learning plan updated'})

    # Default to beginner weeks
    learning_weeks = [
        {
            'week': 1,
            'title': 'Introduction to Programming',
            'description': 'Basic concepts, syntax, and fundamental programming principles',
            'start_date': '2024-12-10',
            'end_date': '2024-12-16'
        },
        {
            'week': 2,
            'title': 'Variables and Data Types',
            'description': 'Understanding different types of data and how to work with variables',
            'start_date': '2024-12-17',
            'end_date': '2024-12-23'
        }
    ]
    
    return render_template('learning_plan.html', learning_weeks=learning_weeks)

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
    recommendations = recommendations_data.get(parent_course, None)
    
    if recommendations is None:
        recommendations = {'videos': [], 'articles': [], 'papers': []}
    
    topic_materials = user_materials.get(topic, [])
    
    # Calculate quiz statistics
    topic_attempts = quiz_attempts.get(topic, {})
    quiz_stats = {
        'attempts_made': topic_attempts.get('attempts', 0),
        'avg_score': sum(topic_attempts.get('scores', [])) / len(topic_attempts.get('scores', [1])) if topic_attempts.get('scores') else 0,
        'attempts_left': topic_attempts.get('max_attempts', 3) - topic_attempts.get('attempts', 0)
    }
    
    app.logger.debug(f"Sending recommendations: {recommendations}")
    
    return render_template('learning_recommendations.html', 
                         recommendations=recommendations,
                         topic=topic,
                         parent_course=parent_course,
                         week_number=week_number,
                         topic_info=topic_info,
                         quiz_attempts=quiz_attempts,
                         quiz_stats=quiz_stats,
                         user_materials=topic_materials)

@app.route('/add-learning-material/<topic>', methods=['POST'])
def add_learning_material(topic):
    if topic not in user_materials:
        user_materials[topic] = []
    
    material_type = request.form.get('material_type')
    title = request.form.get('title')
    description = request.form.get('description')
    
    material_id = f"{len(user_materials[topic])}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    material = {
        'id': material_id,
        'type': material_type,
        'title': title,
        'description': description
    }
    
    if material_type == 'document':
        if 'document' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        file = request.files['document']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{material_id}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            material['filename'] = filename
        else:
            flash('Invalid file type. Please upload PDF or Word documents.', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
    else:
        url = request.form.get('url')
        if not url:
            flash('URL is required for video and article materials', 'error')
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
                return send_file(
                    os.path.join(app.config['UPLOAD_FOLDER'], material['filename']),
                    as_attachment=True
                )
    return 'Material not found', 404

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

@app.route('/mark-recommendation/<topic>/<item_id>', methods=['POST'])
def mark_recommendation(topic, item_id):
    app.logger.debug(f"Mark recommendation request - Topic: {topic}, Item ID: {item_id}")
    
    # Find the parent course for the topic
    parent_course = None
    for course, details in topic_details.items():
        for week_topic in details['topics']:
            if week_topic['title'] == topic:
                parent_course = course
                break
        if parent_course:
            break
    
    if not parent_course:
        app.logger.error(f"Parent course not found for topic: {topic}")
        return jsonify({'status': 'error', 'message': 'Topic not found'}), 404
    
    app.logger.debug(f"Found parent course: {parent_course}")
    
    # Search for the item in the parent course's recommendations
    item_found = False
    course_recommendations = recommendations_data.get(parent_course, {})
    
    for section in ['videos', 'articles', 'papers']:
        for item in course_recommendations.get(section, []):
            if item['id'] == item_id:
                app.logger.debug(f"Found item: {item}")
                item_found = True
                item['completed'] = not item.get('completed', False)
                
                if item['completed']:
                    flash('Congratulations! You can now take a quiz to test your knowledge.', 'success')
                    return jsonify({
                        'status': 'success',
                        'message': 'Item marked as completed',
                        'completed': True
                    })
                else:
                    flash('Progress reset to in progress.', 'info')
                    return jsonify({
                        'status': 'success',
                        'message': 'Item marked as in progress',
                        'completed': False
                    })
    
    if not item_found:
        app.logger.error(f"Item not found - Topic: {topic}, Item ID: {item_id}")
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)