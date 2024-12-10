from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev')  # For development only
app.config['SESSION_TYPE'] = 'filesystem'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User(user_id)
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user_loggedin_page'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Mock signup for demonstration
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_loggedin_page'))
    
    if request.method == 'POST':
        # Mock login for demonstration
        user = User(1)  # In production, verify credentials first
        login_user(user)
        flash('Successfully logged in!', 'success')
        return redirect(url_for('user_loggedin_page'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/user_loggedin_page')
@login_required
def user_loggedin_page():
    user = {
        'name': 'Demo User',
        'email': 'demo@example.com'
    }
    return render_template('user_loggedin_page.html', user=user)

@app.route('/learning-history')
@login_required
def learning_history():
    # Mock learning history data
    learning_history = []  # Add mock data if needed
    return render_template('learning_history.html', learning_history=learning_history)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/learning-credits')
@login_required
def learning_credits():
    return render_template('learning_credits.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
