from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

@app.route('/')
def index():
    return render_template('index.html')

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
