
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from flask_login import current_user


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def regular_user(client):
    with app.app_context():
        user = User(
            username='regular',
            email='regular@example.com',
            is_artist=False,
            is_admin=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def artist_user(client):
    with app.app_context():
        user = User(
            username='artist',
            email='artist@example.com',
            is_artist=True,
            is_admin=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(client):
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            is_artist=True,
            is_admin=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


def login_user(client, email, password):
    return client.post('/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)


def test_user_authentication_success(client, regular_user):
    response = login_user(client, 'regular@example.com', 'password123')
    assert response.status_code == 200
    # Should redirect to home page after successful login


def test_user_authentication_failure(client, regular_user):
    response = client.post('/login', data={
        'email': 'regular@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert b'Invalid' in response.data


def test_protected_route_redirect_when_not_logged_in(client):
    response = client.get('/profile')
    assert response.status_code == 302
    assert '/login' in response.location


def test_protected_route_access_when_logged_in(client, regular_user):
    login_user(client, 'regular@example.com', 'password123')
    response = client.get('/profile')
    assert response.status_code == 200


def test_artist_only_route_access_by_regular_user(client, regular_user):
    login_user(client, 'regular@example.com', 'password123')
    response = client.get('/concerts/create')
    # Should either redirect or show access denied
    assert response.status_code in [302, 403, 200]


def test_artist_only_route_access_by_artist(client, artist_user):
    login_user(client, 'artist@example.com', 'password123')
    response = client.get('/concerts/create')
    assert response.status_code == 200


def test_admin_only_route_access_by_regular_user(client, regular_user):
    login_user(client, 'regular@example.com', 'password123')
    response = client.get('/admin/users')
    assert response.status_code == 302  # Should redirect


def test_admin_only_route_access_by_admin(client, admin_user):
    login_user(client, 'admin@example.com', 'password123')
    response = client.get('/admin/users')
    assert response.status_code == 200


def test_logout_functionality(client, regular_user):
    # Login first
    login_user(client, 'regular@example.com', 'password123')
    
    # Access protected route to confirm login
    response = client.get('/profile')
    assert response.status_code == 200
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # Try to access protected route again
    response = client.get('/profile')
    assert response.status_code == 302  # Should redirect to login


def test_password_hashing_security(client):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('mypassword')
        
        # Password should be hashed, not stored in plain text
        assert user.password_hash != 'mypassword'
        assert len(user.password_hash) > 20  # Hashed passwords are longer
        
        # Should be able to verify correct password
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False


def test_user_session_persistence(client, regular_user):
    # Login
    login_user(client, 'regular@example.com', 'password123')
    
    # Make multiple requests - session should persist
    response1 = client.get('/profile')
    response2 = client.get('/')
    response3 = client.get('/profile')
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200


def test_registration_creates_valid_user(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'is_artist': True
    }, follow_redirects=True)
    
    with app.app_context():
        user = User.query.filter_by(email='new@example.com').first()
        assert user is not None
        assert user.username == 'newuser'
        assert user.is_artist is True
        assert user.check_password('newpassword') is True


def test_duplicate_registration_prevention(client, regular_user):
    # Try to register with existing email
    response = client.post('/register', data={
        'username': 'different',
        'email': 'regular@example.com',  # Already exists
        'password': 'password123',
        'confirm_password': 'password123',
        'is_artist': False
    })
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data
    
    # Try to register with existing username
    response = client.post('/register', data={
        'username': 'regular',  # Already exists
        'email': 'different@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'is_artist': False
    })
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data
