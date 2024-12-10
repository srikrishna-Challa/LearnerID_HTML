import os
import logging
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, LearningPreference, LearningPath, LearningModule

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# Configure database
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

logger.info(f"Database URL configured: {'postgresql://' + database_url.split('postgresql://')[-1] if database_url else 'Not set'}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

# Create database tables
def init_db():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise

# Initialize database tables
with app.app_context():
    init_db()

@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('user_loggedin_page'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return "An error occurred", 500

@app.route('/user_loggedin_page')
@login_required
def user_loggedin_page():
    try:
        return render_template('user_loggedin_page.html', user=current_user)
    except Exception as e:
        logger.error(f"Error in user_loggedin_page route: {e}")
        return "An error occurred", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['username']).first()
            if user and check_password_hash(user.password_hash, request.form['password']):
                login_user(user)
                return redirect(url_for('user_loggedin_page'))
            flash('Invalid username or password')
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login route: {e}")
        return "An error occurred", 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            if User.query.filter_by(email=request.form['email']).first():
                flash('Email address already exists')
                return redirect(url_for('signup'))
            
            user = User(
                email=request.form['email'],
                password_hash=generate_password_hash(request.form['password']),
                name=f"{request.form['first_name']} {request.form['last_name']}"
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('user_loggedin_page'))
        return render_template('signup.html')
    except Exception as e:
        logger.error(f"Error in signup route: {e}")
        db.session.rollback()
        return "An error occurred", 500

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in logout route: {e}")
        return "An error occurred", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)