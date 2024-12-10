from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    learning_preferences = db.relationship('LearningPreference', backref='user', lazy=True)

class LearningPreference(db.Model):
    __tablename__ = 'learning_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level = db.Column(db.String(50))  # beginner, intermediate, advanced
    goal = db.Column(db.String(50))   # new_skill, career, certification
    style = db.Column(db.String(50))  # visual, auditory, reading, kinesthetic
    time_commitment = db.Column(db.String(50))  # less_than_2, 2_to_5, 5_to_10
    target_outcome = db.Column(db.String(100))
    content_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(50))
    estimated_duration = db.Column(db.Integer)  # in weeks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modules = db.relationship('LearningModule', backref='learning_path', lazy=True)

class LearningModule(db.Model):
    __tablename__ = 'learning_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
