from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    
    def __init__(self, username):
        self.username = username

class LearningHistory(db.Model):
    __tablename__ = 'learning_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'In Progress' or 'Completed'
    progress = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    completion_date = db.Column(db.DateTime)

class LearningCredit(db.Model):
    __tablename__ = 'learning_credits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    credits = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # Find or create user
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            
            # Log in the user
            login_user(user)
            
            # Create sample learning history if none exists
            if not LearningHistory.query.filter_by(user_id=user.id).first():
                sample_topics = [
                    ("Python Programming", "In Progress", 65),
                    ("Web Development", "Completed", 100),
                    ("Data Science", "In Progress", 30)
                ]
                for topic, status, progress in sample_topics:
                    history = LearningHistory(
                        user_id=user.id,
                        topic=topic,
                        status=status,
                        progress=progress
                    )
                    db.session.add(history)
                
                # Create initial learning credits
                if not LearningCredit.query.filter_by(user_id=user.id).first():
                    credits = LearningCredit(user_id=user.id, credits=100)  # Start with 100 credits
                    db.session.add(credits)
                
                db.session.commit()
            
            flash('Successfully logged in!', 'success')
            return redirect(url_for('user_loggedin_page'))
        else:
            flash('Username is required', 'error')
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/user-loggedin')
@login_required
def user_loggedin_page():
    return render_template('user_loggedin_page.html', user=current_user)

@app.route('/learning-history')
@login_required
def learning_history():
    # Get user's learning history
    history_items = LearningHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('learning_history.html', 
                         user=current_user,
                         learning_history=history_items,
                         weekly_readings=[])

@app.route('/learning-credits')
@login_required
def learning_credits():
    # Get user's learning credits
    credits = LearningCredit.query.filter_by(user_id=current_user.id).first()
    if not credits:
        credits = LearningCredit(user_id=current_user.id, credits=0)
        db.session.add(credits)
        db.session.commit()
    return render_template('learning_credits.html', user=current_user, credits=credits)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
