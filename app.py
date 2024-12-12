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
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([name, email, password]):
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating user: {str(e)}")
            flash('Error creating account', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('user_loggedin_page'))
        
        flash('Invalid email or password', 'error')
    
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