from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager, UserMixin
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev')  # For development only
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    if 'user_id' in session:
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
    if request.method == 'POST':
        # Mock login for demonstration
        session['user_id'] = 1
        flash('Successfully logged in!', 'success')
        return redirect(url_for('user_loggedin_page'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/user_loggedin_page')
def user_loggedin_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = {
        'name': 'Demo User',
        'email': 'demo@example.com'
    }
    return render_template('user_loggedin_page.html', user=user)

@app.route('/learning-history')
def learning_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('learning_history.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/learning-credits')
def learning_credits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
