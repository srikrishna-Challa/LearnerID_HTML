from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Configure SQLAlchemy with PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user_loggedin_page'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            # Create new user if doesn't exist
            try:
                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                logger.info(f"Created new user: {username}")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                flash('Error creating account', 'error')
                return redirect(url_for('login'))
        
        login_user(user)
        logger.info(f"User logged in: {username}")
        return redirect(url_for('user_loggedin_page'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            logger.info(f"New user signed up: {username}")
            return redirect(url_for('user_loggedin_page'))
        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            flash('Error creating account', 'error')
            
    return render_template('signup.html')

@app.route('/user-loggedin')
@login_required
def user_loggedin_page():
    return render_template('user_loggedin_page.html', user=current_user)

@app.route('/learning-history')
@login_required
def learning_history():
    # Sample data for demonstration
    learning_history = [
        {
            'topic': 'Python Programming',
            'level': 'Intermediate',
            'progress': 75,
            'status': 'In Progress',
            'start_date': '2024-12-01',
            'total_duration': '20 hours'
        },
        {
            'topic': 'Web Development',
            'level': 'Advanced',
            'progress': 100,
            'status': 'Completed',
            'start_date': '2024-11-15',
            'completion_date': '2024-12-10',
            'total_duration': '40 hours',
            'achievements': ['Frontend Master', 'Backend Expert']
        }
    ]
    
    weekly_readings = [
        {
            'start_date': '2024-12-06',
            'end_date': '2024-12-12',
            'total_readings': 5,
            'total_duration': '8 hours',
            'topics': ['Python', 'JavaScript', 'HTML'],
            'readings': [
                {
                    'title': 'Advanced Python Concepts',
                    'summary': 'Deep dive into Python decorators and context managers'
                },
                {
                    'title': 'Modern JavaScript Features',
                    'summary': 'Understanding ES6+ features and best practices'
                }
            ]
        }
    ]
    
    return render_template('learning_history.html', 
                         user=current_user,
                         learning_history=learning_history,
                         weekly_readings=weekly_readings)

@app.route('/learning-credits')
@login_required
def learning_credits():
    return render_template('learning_credits.html', user=current_user)

@app.route('/create-learning-journal', methods=['GET', 'POST'])
@login_required
def create_learning_journal():
    if request.method == 'POST':
        flash('Journal entry created successfully!', 'success')
        return redirect(url_for('learning_history'))
    return render_template('learning_journal.html', user=current_user, entries=[])

@app.route('/inbox')
@login_required
def inbox():
    emails = [
        {
            'subject': 'Welcome to LearnerID',
            'sender': 'support@learnerid.com',
            'preview': 'Welcome to your learning journey...',
            'date': '2024-12-13',
            'unread': True
        }
    ]
    return render_template('inbox.html', user=current_user, emails=emails)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html', user=current_user)

@app.route('/learning-plan')
@login_required
def learning_plan():
    learning_topics = [
        {
            'title': 'Python Programming',
            'description': 'Learn Python from basics to advanced concepts',
            'time_required': 20,
            'objectives': ['Basic syntax', 'Functions', 'Object-oriented programming']
        },
        {
            'title': 'Web Development',
            'description': 'Master web development fundamentals',
            'time_required': 30,
            'objectives': ['HTML', 'CSS', 'JavaScript']
        }
    ]
    return render_template('learning_plan.html', learning_topics=learning_topics)

@app.route('/my-learning-details/<topic>')
@login_required
def my_learning_details(topic):
    details = {
        'title': topic,
        'level': 'Intermediate',
        'start_date': '2024-12-01',
        'progress': 75,
        'topics': [
            {
                'week': 1,
                'title': 'Getting Started',
                'progress': 100,
                'status': 'Completed',
                'contents': ['Introduction', 'Setup Environment', 'Basic Concepts']
            },
            {
                'week': 2,
                'title': 'Advanced Topics',
                'progress': 50,
                'status': 'In Progress',
                'contents': ['Advanced Features', 'Best Practices', 'Real-world Applications']
            }
        ]
    }
    return render_template('my_learning_details.html', user=current_user, details=details)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
