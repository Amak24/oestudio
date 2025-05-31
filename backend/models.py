from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_picture = db.Column(db.String(256), default="https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png")
    bio = db.Column(db.String(500))
    is_artist = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Concert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(256), nullable=False)
    thumbnail_url = db.Column(db.String(256), nullable=False)
    genre = db.Column(db.String(64))
    duration = db.Column(db.Integer)  # Duration in seconds
    is_live = db.Column(db.Boolean, default=False)
    scheduled_for = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    artist = db.relationship('User', backref=db.backref('concerts', lazy='dynamic'))
    comments = db.relationship('Comment', backref='concert', lazy='dynamic', cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='concert', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Concert {self.title}>'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username}>'


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'concert_id', name='unique_user_concert_like'),)
    
    def __repr__(self):
        return f'<Like by {self.user.username} on concert {self.concert.title}>'
