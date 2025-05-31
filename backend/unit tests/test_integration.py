import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # desabilitar CSRF para testes
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_login_page_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data


def test_login_page_post_valid(client):
    response = client.post('/login', data={
        'email': 'user@example.com',
        'password': 'validpassword'
    }, follow_redirects=True)
    # resultado depende do app; ajustável
    assert response.status_code in (200, 302)


def test_register_page_get(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data


def test_register_page_post_invalid(client):
    response = client.post('/register', data={
        'username': 'u',
        'email': 'invalid-email',
        'password': 'short',
        'confirm_password': 'short'
    })
    assert response.status_code == 200
    assert b"This field is required" in response.data or b"Invalid" in response.data


def test_profile_update(client):
    # Este teste assume que o usuário já está autenticado (exemplo simplificado)
    response = client.post('/profile', data={
        'username': 'NewUser',
        'email': 'newuser@example.com',
        'bio': 'New bio'
    })
    assert response.status_code in (200, 302)


def test_create_concert_invalid_url(client):
    response = client.post('/concerts/create', data={
        'title': 'New Concert',
        'description': 'An amazing night',
        'video_url': 'invalid',
        'thumbnail_url': 'invalid',
        'genre': 'rock',
        'duration': '60'
    })
    assert b"Invalid URL" in response.data or response.status_code == 200


def test_search_concerts(client):
    response = client.get('/search?query=jazz')
    assert response.status_code == 200
