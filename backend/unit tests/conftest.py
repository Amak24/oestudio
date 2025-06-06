
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Concert, Comment, Like


@pytest.fixture(scope='session')
def test_app():
    """Create application for testing."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def test_db(test_app):
    """Create database for testing."""
    db.create_all()
    yield db
    db.drop_all()


@pytest.fixture
def client(test_app, test_db):
    """Create test client."""
    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    """Create test runner."""
    return test_app.test_cli_runner()


# Shared user fixtures
@pytest.fixture
def regular_user(test_db):
    """Create a regular user for testing."""
    user = User(
        username='regular',
        email='regular@example.com',
        is_artist=False,
        is_admin=False
    )
    user.set_password('password123')
    test_db.session.add(user)
    test_db.session.commit()
    return user


@pytest.fixture
def artist_user(test_db):
    """Create an artist user for testing."""
    user = User(
        username='artist',
        email='artist@example.com',
        is_artist=True,
        is_admin=False
    )
    user.set_password('password123')
    test_db.session.add(user)
    test_db.session.commit()
    return user


@pytest.fixture
def admin_user(test_db):
    """Create an admin user for testing."""
    user = User(
        username='admin',
        email='admin@example.com',
        is_artist=True,
        is_admin=True
    )
    user.set_password('password123')
    test_db.session.add(user)
    test_db.session.commit()
    return user


@pytest.fixture
def sample_concert(test_db, artist_user):
    """Create a sample concert for testing."""
    concert = Concert(
        title='Test Concert',
        artist_id=artist_user.id,
        description='A test concert for unit testing',
        video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
        thumbnail_url='https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
        genre='rock',
        duration=180,
        is_live=False
    )
    test_db.session.add(concert)
    test_db.session.commit()
    return concert


@pytest.fixture
def sample_comment(test_db, regular_user, sample_concert):
    """Create a sample comment for testing."""
    comment = Comment(
        content='Great concert!',
        user_id=regular_user.id,
        concert_id=sample_concert.id
    )
    test_db.session.add(comment)
    test_db.session.commit()
    return comment


@pytest.fixture
def sample_like(test_db, regular_user, sample_concert):
    """Create a sample like for testing."""
    like = Like(
        user_id=regular_user.id,
        concert_id=sample_concert.id
    )
    test_db.session.add(like)
    test_db.session.commit()
    return like


def login_user(client, email, password):
    """Helper function to login a user."""
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


def logout_user(client):
    """Helper function to logout a user."""
    return client.get('/logout', follow_redirects=True)
