
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Concert, Comment, Like
import json
from flask_login import login_user


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
def sample_user(client):
    with app.app_context():
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
def admin_user(client):
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_artist=True
        )
        user.set_password('adminpass')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_concert(client, sample_user):
    with app.app_context():
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


def test_home_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'O Est' in response.data


def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data


def test_register_page_get(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data


def test_valid_registration(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'validpassword',
        'confirm_password': 'validpassword',
        'is_artist': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Congratulations' in response.data or b'Sign In' in response.data


def test_invalid_registration_password_mismatch(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password1',
        'confirm_password': 'password2',
        'is_artist': False
    })
    
    assert response.status_code == 200
    assert b'Register' in response.data


def test_duplicate_username_registration(client, sample_user):
    response = client.post('/register', data={
        'username': 'testuser',  # Same as existing user
        'email': 'different@example.com',
        'password': 'validpassword',
        'confirm_password': 'validpassword',
        'is_artist': False
    })
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data


def test_valid_login(client, sample_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_invalid_login(client, sample_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200
    assert b'Invalid' in response.data


def test_logout_redirect(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


def test_profile_requires_login(client):
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login


def test_create_concert_requires_login(client):
    response = client.get('/concerts/create')
    assert response.status_code == 302  # Redirect to login


def test_search_functionality(client, sample_concert):
    response = client.get('/search?query=Test')
    assert response.status_code == 200


def test_search_with_genre_filter(client, sample_concert):
    response = client.get('/search?genre=rock')
    assert response.status_code == 200


def test_concert_detail_page(client, sample_concert):
    response = client.get(f'/concerts/{sample_concert.id}')
    assert response.status_code == 200
    assert b'Test Concert' in response.data


def test_nonexistent_concert_404(client):
    response = client.get('/concerts/999')
    assert response.status_code == 404


def test_api_login_valid(client, sample_user):
    response = client.post('/api/login', 
                          data=json.dumps({
                              'email': 'test@example.com',
                              'password': 'testpassword'
                          }),
                          content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['success'] is True


def test_api_login_invalid(client, sample_user):
    response = client.post('/api/login', 
                          data=json.dumps({
                              'email': 'test@example.com',
                              'password': 'wrongpassword'
                          }),
                          content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 401
    assert data['success'] is False


def test_api_register_valid(client):
    response = client.post('/api/register', 
                          data=json.dumps({
                              'username': 'apiuser',
                              'email': 'api@example.com',
                              'password': 'apipassword'
                          }),
                          content_type='application/json')
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['success'] is True


def test_manage_users_requires_admin(client, sample_user):
    # Login as regular user
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    
    response = client.get('/admin/users')
    assert response.status_code == 302  # Redirect due to lack of admin access


def test_admin_user_management_access(client, admin_user):
    # Login as admin
    client.post('/login', data={
        'email': 'admin@example.com',
        'password': 'adminpass'
    })
    
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'User Management' in response.data


def test_create_user_requires_admin(client, sample_user):
    # Login as regular user
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    })
    
    response = client.get('/admin/create-user')
    assert response.status_code == 302  # Redirect due to lack of admin access


def test_seed_demo_route(client):
    response = client.get('/seed_demo')
    assert response.status_code == 200
    assert b'Demo data seeded successfully' in response.data
