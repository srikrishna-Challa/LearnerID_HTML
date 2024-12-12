from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///learner.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    journal_entries = db.relationship('LearningJournalEntry', backref='user', lazy=True)

class LearningJournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    topic = db.Column(db.String(100))
    notes = db.Column(db.Text)
    urls = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    app.logger.debug("Entering signup route")
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        app.logger.debug(f"Signup attempt for email: {email}")
        
        if not all([name, email, password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        try:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"Successfully created user with email: {email}")
            
            # Log the user in immediately after signup
            session['user_id'] = user.id
            session.modified = True
            flash('Account created successfully! You are now logged in.', 'success')
            return redirect(url_for('user_loggedin_page'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {str(e)}")
            flash('Error creating account', 'error')
            return render_template('signup.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug("Entering login route")
    
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        app.logger.debug(f"User already logged in with session id: {session['user_id']}")
        return redirect(url_for('user_loggedin_page'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        app.logger.debug(f"Login attempt for email: {email}")
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')
        
        # Create test user if it doesn't exist
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            app.logger.debug("Creating test user")
            test_user = User(
                name="Test User",
                email="test@example.com",
                password_hash=generate_password_hash("password123")
            )
            db.session.add(test_user)
            db.session.commit()
        
        user = User.query.filter_by(email=email).first()
        app.logger.debug(f"Found user: {user is not None}")
        
        if user:
            app.logger.debug("Checking password hash")
            if check_password_hash(user.password_hash, password):
                app.logger.debug("Password matched")
                session['user_id'] = user.id
                session.modified = True
                flash('Logged in successfully!', 'success')
                
                # Redirect to the page user was trying to access, or dashboard by default
                next_page = request.args.get('next')
                app.logger.debug(f"Next page: {next_page}")
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('user_loggedin_page'))
            else:
                app.logger.debug("Password mismatch")
        
        flash('Invalid email or password', 'error')
        app.logger.warning(f"Failed login attempt for email: {email}")
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/user-logged-in')
def user_loggedin_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/learning-journal', methods=['GET', 'POST'])
def create_learning_journal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        topic = request.form.get('topic')
        notes = request.form.get('notes')
        urls = request.form.getlist('urls[]')
        
        # Filter out empty URLs
        urls = [url for url in urls if url.strip()]
        
        if not title:
            flash('Title is required', 'error')
            return redirect(url_for('create_learning_journal'))
        
        entry = LearningJournalEntry(
            title=title,
            description=description,
            topic=topic,
            notes=notes,
            urls=urls,
            user_id=session['user_id']
        )
        
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Entry created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating entry: {str(e)}")
            flash('Error creating entry', 'error')
        
        return redirect(url_for('create_learning_journal'))
    
    # Get all entries for the current user
    entries = LearningJournalEntry.query.filter_by(user_id=session['user_id']).order_by(LearningJournalEntry.created_at.desc()).all()
    
    # Get unique topics for the filter dropdown
    topics = db.session.query(LearningJournalEntry.topic).distinct().all()
    topics = [topic[0] for topic in topics if topic[0]]  # Remove None values
    
    return render_template('learning_journal.html', 
                         user=user,
                         entries=entries,
                         topics=topics)

@app.route('/delete-entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    entry = LearningJournalEntry.query.get_or_404(entry_id)
    
    # Verify the entry belongs to the current user
    if entry.user_id != session['user_id']:
        flash('You are not authorized to delete this entry.', 'error')
        return redirect(url_for('create_learning_journal'))
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting entry: {str(e)}")
        flash('Error deleting entry', 'error')
    
    return redirect(url_for('create_learning_journal'))

@app.route('/learning-history')
def learning_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('learning_history.html', user=user)

@app.route('/learning-credits')
def learning_credits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('learning_credits.html', user=user)

@app.route('/learning-plan')
def learning_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('learning_plan.html', user=user)

@app.route('/learning-recommendations/<topic>')
def learning_recommendations(topic):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('learning_recommendations.html', user=user, topic=topic)

@app.route('/how-it-works')
def how_it_works():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('how_it_works.html', user=user)

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('about.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
