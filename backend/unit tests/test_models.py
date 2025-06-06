
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Concert, Comment, Like
from datetime import datetime


@pytest.fixture
def app_context():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def sample_user(app_context):
    user = User(
        username='testuser',
        email='test@example.com',
        is_artist=True
    )
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_concert(app_context, sample_user):
    concert = Concert(
        title='Test Concert',
        artist_id=sample_user.id,
        description='A test concert',
        video_url='https://example.com/video',
        thumbnail_url='https://example.com/thumb',
        genre='rock',
        duration=120,
        is_live=False
    )
    db.session.add(concert)
    db.session.commit()
    return concert


def test_user_creation(app_context):
    user = User(username='newuser', email='new@example.com')
    user.set_password('password123')
    
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'newuser'
    assert user.email == 'new@example.com'
    assert user.check_password('password123') is True
    assert user.check_password('wrongpassword') is False


def test_user_password_hashing(app_context):
    user = User(username='hashtest', email='hash@example.com')
    user.set_password('mypassword')
    
    assert user.password_hash != 'mypassword'
    assert user.check_password('mypassword') is True
    assert user.check_password('wrongpass') is False


def test_user_artist_flag(app_context):
    regular_user = User(username='regular', email='regular@example.com')
    artist_user = User(username='artist', email='artist@example.com', is_artist=True)
    
    assert regular_user.is_artist is False
    assert artist_user.is_artist is True


def test_concert_creation(app_context, sample_user):
    concert = Concert(
        title='New Concert',
        artist_id=sample_user.id,
        description='Amazing performance',
        video_url='https://youtube.com/watch?v=123',
        thumbnail_url='https://img.youtube.com/vi/123/maxresdefault.jpg',
        genre='jazz',
        duration=180,
        is_live=True,
        scheduled_for=datetime(2025, 12, 25, 20, 0)
    )
    
    db.session.add(concert)
    db.session.commit()
    
    assert concert.id is not None
    assert concert.title == 'New Concert'
    assert concert.artist_id == sample_user.id
    assert concert.genre == 'jazz'
    assert concert.is_live is True


def test_concert_artist_relationship(app_context, sample_user, sample_concert):
    assert sample_concert.artist == sample_user
    assert sample_concert in sample_user.concerts


def test_comment_creation(app_context, sample_user, sample_concert):
    comment = Comment(
        content='Great performance!',
        user_id=sample_user.id,
        concert_id=sample_concert.id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    assert comment.id is not None
    assert comment.content == 'Great performance!'
    assert comment.author == sample_user
    assert comment.concert == sample_concert


def test_like_creation(app_context, sample_user, sample_concert):
    like = Like(
        user_id=sample_user.id,
        concert_id=sample_concert.id
    )
    
    db.session.add(like)
    db.session.commit()
    
    assert like.id is not None
    assert like.user == sample_user
    assert like.concert == sample_concert


def test_user_cascade_delete(app_context, sample_user, sample_concert):
    # Create comment and like
    comment = Comment(content='Test comment', user_id=sample_user.id, concert_id=sample_concert.id)
    like = Like(user_id=sample_user.id, concert_id=sample_concert.id)
    
    db.session.add(comment)
    db.session.add(like)
    db.session.commit()
    
    comment_id = comment.id
    like_id = like.id
    
    # Delete user should cascade delete comments and likes
    db.session.delete(sample_user)
    db.session.commit()
    
    assert Comment.query.get(comment_id) is None
    assert Like.query.get(like_id) is None


def test_concert_cascade_delete(app_context, sample_user, sample_concert):
    # Create comment and like
    comment = Comment(content='Test comment', user_id=sample_user.id, concert_id=sample_concert.id)
    like = Like(user_id=sample_user.id, concert_id=sample_concert.id)
    
    db.session.add(comment)
    db.session.add(like)
    db.session.commit()
    
    comment_id = comment.id
    like_id = like.id
    
    # Delete concert should cascade delete comments and likes
    db.session.delete(sample_concert)
    db.session.commit()
    
    assert Comment.query.get(comment_id) is None
    assert Like.query.get(like_id) is None


def test_user_repr(app_context, sample_user):
    assert repr(sample_user) == '<User testuser>'


def test_concert_repr(app_context, sample_concert):
    assert repr(sample_concert) == '<Concert Test Concert>'
