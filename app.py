import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # TODO: Move to environment variable
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Mock user materials storage
user_materials = {}  # Format: {topic: [{'id': str, 'type': str, 'title': str, 'description': str, 'url': str, 'filename': str}]}

# Mock quiz attempts storage
quiz_attempts = {}  # Format: {topic: {'attempts': int, 'scores': [float], 'max_attempts': int}}
# Mock topic details storage
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
                'progress': 45,
                'contents': [
                    'What is Data Science?',
                    'Data Collection and Preprocessing',
                    'Exploratory Data Analysis',
                    'Basic Statistics'
                ]
            },
            {
                'week': 2,
                'title': 'Data Visualization',
                'status': 'Not Started',
                'progress': 0,
                'contents': [
                    'Visualization Principles',
                    'Charts and Graphs',
                    'Interactive Visualizations',
                    'Storytelling with Data'
                ]
            }
        ]
    }
}

@app.route('/quiz/<topic>/<item_id>')
def show_quiz(topic, item_id):
    if topic not in quiz_data:
        flash('Quiz not available for this topic', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    # Initialize attempts tracking if not exists
    if topic not in quiz_attempts:
        quiz_attempts[topic] = {
            'attempts': 0,
            'scores': [],
            'max_attempts': 3
        }
    
    attempts_info = quiz_attempts[topic]
    avg_score = sum(attempts_info['scores']) / len(attempts_info['scores']) if attempts_info['scores'] else 0
    attempts_left = attempts_info['max_attempts'] - attempts_info['attempts']
    
    questions = quiz_data[topic]['questions']
    return render_template('quiz.html', 
                         topic=topic, 
                         item_id=item_id, 
                         questions=questions,
                         attempts=attempts_info['attempts'],
                         avg_score=round(avg_score, 2),
                         attempts_left=attempts_left)

@app.route('/submit-quiz/<topic>/<item_id>', methods=['POST'])
def submit_quiz(topic, item_id):
    if topic not in quiz_data:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404
    
    # Check if maximum attempts reached
    if quiz_attempts[topic]['attempts'] >= quiz_attempts[topic]['max_attempts']:
        flash('You have reached the maximum number of attempts for this quiz.', 'error')
        return redirect(url_for('learning_recommendations', topic=topic))
    
    questions = quiz_data[topic]['questions']
    correct_count = 0
    
    # Grade the quiz
    for i in range(len(questions)):
        user_answer = request.form.get(f'q{i+1}')
        if user_answer and int(user_answer) == questions[i]['correct']:
            correct_count += 1
    
    # Calculate score as percentage
    score = (correct_count / len(questions)) * 100
    
    # Update attempts tracking
    quiz_attempts[topic]['attempts'] += 1
    quiz_attempts[topic]['scores'].append(score)
    
    # Check if passed
    passed = correct_count >= quiz_data[topic]['passing_score']
    
    if passed:
        # Find and update the item's credits status
        for section in recommendations_data[topic].values():
            for item in section:
                if item['id'] == item_id:
                    item['credits_unlocked'] = True
        
        flash(f'Congratulations! You passed the quiz with {correct_count} correct answers. Learning credits have been unlocked!', 'success')
    else:
        attempts_left = quiz_attempts[topic]['max_attempts'] - quiz_attempts[topic]['attempts']
        flash(f'You got {correct_count} answers correct. You need {quiz_data[topic]["passing_score"]} to pass. You have {attempts_left} attempts left!', 'error')
    
    return redirect(url_for('learning_recommendations', topic=topic))

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

    # Default to beginner weeks
    learning_weeks = [
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
    
    return render_template('learning_plan.html', learning_weeks=learning_weeks)

@app.route('/my-learning-details/<topic>')
def my_learning_details(topic):
    details = topic_details.get(topic)
    if not details:
        flash('Topic not found', 'error')
        return redirect(url_for('learning_history'))
        
    return render_template('my_learning_details.html', details=details)

@app.route('/learning-recommendations/<topic>')
def learning_recommendations(topic):
    if topic not in quiz_attempts:
        quiz_attempts[topic] = {'attempts': 0, 'scores': [], 'max_attempts': 3}
    
    recommendations = recommendations_data.get(topic, {
        'videos': [],
        'articles': [],
        'papers': []
    })
    topic_materials = user_materials.get(topic, [])
    
    return render_template('learning_recommendations.html', 
                         recommendations=recommendations, 
                         topic=topic,
                         quiz_attempts=quiz_attempts,
                         user_materials=topic_materials)

@app.route('/add-learning-material/<topic>', methods=['POST'])
def add_learning_material(topic):
    if topic not in user_materials:
        user_materials[topic] = []
    
    material_type = request.form.get('material_type')
    title = request.form.get('title')
    description = request.form.get('description')
    
    material_id = f"{len(user_materials[topic])}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    material = {
        'id': material_id,
        'type': material_type,
        'title': title,
        'description': description
    }
    
    if material_type == 'document':
        if 'document' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        file = request.files['document']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{material_id}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            material['filename'] = filename
        else:
            flash('Invalid file type. Please upload PDF or Word documents.', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
    else:
        url = request.form.get('url')
        if not url:
            flash('URL is required for video and article materials', 'error')
            return redirect(url_for('learning_recommendations', topic=topic))
        material['url'] = url
    
    user_materials[topic].append(material)
    flash('Learning material added successfully!', 'success')
    return redirect(url_for('learning_recommendations', topic=topic))

@app.route('/download-material/<material_id>')
def download_material(material_id):
    for materials in user_materials.values():
        for material in materials:
            if material['id'] == material_id and material['type'] == 'document':
                return send_file(
                    os.path.join(app.config['UPLOAD_FOLDER'], material['filename']),
                    as_attachment=True
                )
    return 'Material not found', 404

@app.route('/delete-material/<material_id>', methods=['POST'])
def delete_material(material_id):
    for topic, materials in user_materials.items():
        for i, material in enumerate(materials):
            if material['id'] == material_id:
                if material['type'] == 'document':
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], material['filename']))
                    except:
                        pass
                materials.pop(i)
                flash('Material deleted successfully!', 'success')
                return redirect(url_for('learning_recommendations', topic=topic))
    
    flash('Material not found', 'error')
    return redirect(request.referrer)

@app.route('/mark-recommendation/<topic>/<item_id>', methods=['POST'])
def mark_recommendation(topic, item_id):
    item_found = False
    for section in ['videos', 'articles', 'papers']:
        for item in recommendations_data.get(topic, {}).get(section, []):
            if item['id'] == item_id:
                item_found = True
                item['completed'] = not item.get('completed', False)
                if item['completed']:
                    flash('Congratulations for completing the topic! You can take a quick test to evaluate your knowledge on this topic.', 'success')
                    return jsonify({
                        'status': 'success',
                        'message': 'Topic marked as completed',
                        'completed': True
                    })
                else:
                    flash('Topic status changed to In Progress.', 'info')
                    return jsonify({
                        'status': 'success',
                        'message': 'Topic marked as in progress',
                        'completed': False
                    })
    
    if not item_found:
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)