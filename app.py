from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Basic configuration
app.secret_key = 'dev'  # For development only

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_loggedin_page')
def user_loggedin_page():
    user = {
        'name': 'Demo User',
        'email': 'demo@example.com'
    }
    return render_template('user_loggedin_page.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
