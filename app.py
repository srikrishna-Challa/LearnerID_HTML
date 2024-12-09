from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

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
        # Handle login form submission here
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
        # Handle signup form submission here
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

    # In a real application, we would use the user's preferences to generate a customized plan
    # For now, we'll demonstrate different content based on the level
    beginner_weeks = [
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
    
    intermediate_weeks = [
        {
            'week': 1,
            'title': 'Advanced Data Structures',
            'description': 'Deep dive into complex data structures and their applications',
            'start_date': '2024-12-10',
            'end_date': '2024-12-16'
        },
        {
            'week': 2,
            'title': 'Algorithm Design',
            'description': 'Understanding and implementing efficient algorithms',
            'start_date': '2024-12-17',
            'end_date': '2024-12-23'
        }
    ]
    
    advanced_weeks = [
        {
            'week': 1,
            'title': 'System Architecture',
            'description': 'Designing and implementing complex software systems',
            'start_date': '2024-12-10',
            'end_date': '2024-12-16'
        },
        {
            'week': 2,
            'title': 'Advanced Topics',
            'description': 'Exploring cutting-edge technologies and methodologies',
            'start_date': '2024-12-17',
            'end_date': '2024-12-23'
        }
    ]
    
    # Default to beginner weeks
    learning_weeks = beginner_weeks
    
    return render_template('learning_plan.html', learning_weeks=learning_weeks)

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

@app.route('/my-learning-details/<topic>')
def my_learning_details(topic):
    # Mock data for demonstration
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
    
    details = topic_details.get(topic)
    if not details:
        flash('Topic not found', 'error')
        return redirect(url_for('learning_history'))
        
    return render_template('my_learning_details.html', details=details)
