import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # TODO: Move to environment variable
logging.basicConfig(level=logging.DEBUG)

# Topic details for learning paths
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
            },
            {
                'week': 3,
                'title': 'Web Development Fundamentals',
                'status': 'Not Started',
                'progress': 0,
                'contents': [
                    'HTML and CSS',
                    'JavaScript Basics',
                    'DOM Manipulation',
                    'Web APIs'
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
                'progress': 75,
                'contents': [
                    'What is Data Science?',
                    'Data Collection Methods',
                    'Data Cleaning',
                    'Basic Statistics'
                ]
            },
            {
                'week': 2,
                'title': 'Data Analysis Tools',
                'status': 'Not Started',
                'progress': 0,
                'contents': [
                    'Python for Data Analysis',
                    'Pandas Library',
                    'NumPy Basics',
                    'Data Visualization'
                ]
            }
        ]
    }
}

# Mock recommendations data
recommendations_data = {
    'Introduction to Programming': {
        'videos': [
            {
                'id': 'v1',
                'title': 'Introduction to Programming Concepts',
                'description': 'A comprehensive introduction to programming concepts',
                'duration': '45 min',
                'url': 'https://example.com/video1',
                'completed': False,
                'credits_unlocked': False
            },
            {
                'id': 'v2',
                'title': 'Data Types and Variables',
                'description': 'Understanding different types of data in programming',
                'duration': '30 min',
                'url': 'https://example.com/video2',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'articles': [
            {
                'id': 'a1',
                'title': 'Getting Started with Programming',
                'description': 'A beginner-friendly guide to programming',
                'reading_time': '10 min',
                'url': 'https://example.com/article1',
                'completed': False,
                'credits_unlocked': False
            }
        ],
        'papers': [
            {
                'id': 'p1',
                'title': 'Modern Programming Paradigms',
                'authors': 'John Doe, Jane Smith',
                'abstract': 'An overview of current programming paradigms',
                'published_date': '2024',
                'url': 'https://example.com/paper1',
                'completed': False,
                'credits_unlocked': False
            }
        ]
    }
}

# Mock quiz data
quiz_data = {
    'Introduction to Programming': {
        'questions': [
            {
                'text': 'What is a variable in programming?',
                'options': [
                    'A fixed value that cannot change',
                    'A container for storing data values',
                    'A type of loop',
                    'A programming language'
                ],
                'correct': 1
            },
            {
                'text': 'Which of the following is a correct way to comment code in Python?',
                'options': [
                    '// This is a comment',
                    '/* This is a comment */',
                    '# This is a comment',
                    '-- This is a comment'
                ],
                'correct': 2
            },
            {
                'text': 'What is the purpose of a loop in programming?',
                'options': [
                    'To store multiple values',
                    'To repeat a block of code',
                    'To define functions',
                    'To import libraries'
                ],
                'correct': 1
            },
            {
                'text': 'What is the result of 5 + "3" in Python?',
                'options': [
                    '8',
                    '53',
                    'Error',
                    'None'
                ],
                'correct': 2
            },
            {
                'text': 'Which data type is used to store a sequence of characters?',
                'options': [
                    'Integer',
                    'Float',
                    'Boolean',
                    'String'
                ],
                'correct': 3
            },
            {
                'text': 'What is the purpose of an if statement?',
                'options': [
                    'To define a function',
                    'To create a loop',
                    'To make decisions in code',
                    'To store data'
                ],
                'correct': 2
            },
            {
                'text': 'What does len() function do in Python?',
                'options': [
                    'Converts to lowercase',
                    'Returns the length',
                    'Rounds a number',
                    'Creates a list'
                ],
                'correct': 1
            },
            {
                'text': 'Which operator is used for exponentiation in Python?',
                'options': [
                    '^',
                    '**',
                    '^^',
                    '//'
                ],
                'correct': 1
            },
            {
                'text': 'What is the correct way to define a function in Python?',
                'options': [
                    'function myFunc():',
                    'def myFunc():',
                    'func myFunc():',
                    'define myFunc():'
                ],
                'correct': 1
            },
            {
                'text': 'Which of these is not a valid variable name in Python?',
                'options': [
                    'my_variable',
                    '_hidden',
                    '2start',
                    'camelCase'
                ],
                'correct': 2
            }
        ],
        'passing_score': 7  # Need 7 out of 10 correct to pass
    }
}

@app.route('/quiz/<topic>/<item_id>')
def show_quiz(topic, item_id):
    if topic not in quiz_data:
        flash('Quiz not available for this topic', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    questions = quiz_data[topic]['questions']
    return render_template('quiz.html', topic=topic, item_id=item_id, questions=questions)

@app.route('/submit-quiz/<topic>/<item_id>', methods=['POST'])
def submit_quiz(topic, item_id):
    if topic not in quiz_data:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404
    
    questions = quiz_data[topic]['questions']
    correct_count = 0
    
    # Grade the quiz
    for i in range(len(questions)):
        user_answer = request.form.get(f'q{i+1}')
        if user_answer and int(user_answer) == questions[i]['correct']:
            correct_count += 1
    
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
        flash(f'You got {correct_count} answers correct. You need {quiz_data[topic]["passing_score"]} to pass. Try again!', 'error')
    
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # TODO: Add authentication check
    return render_template('dashboard.html')

@app.route('/mails')
def mails():
    # TODO: Add authentication check
    return render_template('dashboard.html')  # We'll create a separate template later

@app.route('/learning-credits')
def learning_credits():
    # TODO: Add authentication check
    return render_template('dashboard.html')  # We'll create a separate template later

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
        
        # TODO: Add authentication logic
        flash('Login functionality will be implemented soon.')
        return redirect(url_for('index'))
    
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
        
    return render_template('my_learning_details.html', details=details)

@app.route('/learning-recommendations/<topic>')
def learning_recommendations(topic):
    recommendations = recommendations_data.get(topic, {
        'videos': [],
        'articles': [],
        'papers': []
    })
    return render_template('learning_recommendations.html', recommendations=recommendations, topic=topic)

@app.route('/mark-recommendation/<topic>/<item_id>', methods=['POST'])
def mark_recommendation(topic, item_id):
    if topic not in recommendations_data:
        return jsonify({'status': 'error', 'message': 'Topic not found'}), 404
    
    # Find and toggle the completion status of the item
    item_found = False
    for section in recommendations_data[topic].values():
        for item in section:
            if item['id'] == item_id:
                item['completed'] = not item['completed']
                item_found = True
                if item['completed']:
                    flash('Congratulations for completing the topic! You can take a quick test to evaluate your knowledge on this topic.', 'success')
                    return jsonify({
                        'status': 'success',
                        'message': 'Topic marked as completed',
                        'completed': True
                    })
                else:
                    flash('Topic status changed to In Progress.', 'info')
                    return jsonify({
                        'status': 'success',
                        'message': 'Topic marked as in progress',
                        'completed': False
                    })
    
    if not item_found:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404

@app.route('/learning-history')
def learning_history():
    # Mock data for demonstration
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
    return render_template('learning_history.html', learning_history=learning_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)