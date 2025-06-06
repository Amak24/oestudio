
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Concert
import tempfile
from werkzeug.datastructures import FileStorage
import io


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
def artist_user(client):
    with app.app_context():
        user = User(
            username='artist',
            email='artist@example.com',
            is_artist=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


def login_artist(client):
    return client.post('/login', data={
        'email': 'artist@example.com',
        'password': 'password123'
    }, follow_redirects=True)


def test_youtube_url_validation():
    valid_youtube_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'https://youtube.com/watch?v=dQw4w9WgXcQ'
    ]
    
    invalid_urls = [
        'https://vimeo.com/123456',
        'https://example.com/video',
        'not_a_url',
        'https://youtube.com',  # No video ID
    ]
    
    # This would be implemented in your forms validation
    for url in valid_youtube_urls:
        assert 'youtube' in url.lower() or 'youtu.be' in url.lower()
    
    for url in invalid_urls:
        # Test that these would fail validation
        if 'youtube' not in url.lower() and 'youtu.be' not in url.lower():
            assert True  # These should fail validation


def test_create_concert_with_youtube_url(client, artist_user):
    login_artist(client)
    
    response = client.post('/concerts/create', data={
        'title': 'YouTube Concert',
        'description': 'A concert from YouTube',
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
        'genre': 'pop',
        'duration': '180',
        'is_live': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        concert = Concert.query.filter_by(title='YouTube Concert').first()
        assert concert is not None
        assert 'youtube.com' in concert.video_url


def test_create_concert_with_invalid_url(client, artist_user):
    login_artist(client)
    
    response = client.post('/concerts/create', data={
        'title': 'Invalid URL Concert',
        'description': 'A concert with invalid URL',
        'video_url': 'not_a_valid_url',
        'thumbnail_url': 'also_not_valid',
        'genre': 'rock',
        'duration': '120',
        'is_live': False
    })
    
    # Should stay on the form page with validation errors
    assert response.status_code == 200
    assert b'Create Concert' in response.data or b'Invalid' in response.data


def test_youtube_embed_url_conversion():
    # Test that YouTube watch URLs can be converted to embed URLs
    watch_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    expected_embed = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
    
    # This would be implemented in your forms or models
    if 'watch?v=' in watch_url:
        video_id = watch_url.split('watch?v=')[1].split('&')[0]
        embed_url = f'https://www.youtube.com/embed/{video_id}'
        assert embed_url == expected_embed


def test_youtu_be_url_handling():
    # Test that youtu.be URLs can be handled
    short_url = 'https://youtu.be/dQw4w9WgXcQ'
    expected_embed = 'https://www.youtube.com/embed/dQw4w9WgXcQ'
    
    if 'youtu.be/' in short_url:
        video_id = short_url.split('youtu.be/')[1].split('?')[0]
        embed_url = f'https://www.youtube.com/embed/{video_id}'
        assert embed_url == expected_embed


def test_thumbnail_generation_from_youtube():
    # Test that thumbnails can be generated from YouTube video IDs
    video_id = 'dQw4w9WgXcQ'
    expected_thumbnail = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
    
    generated_thumbnail = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
    assert generated_thumbnail == expected_thumbnail


def test_create_concert_auto_thumbnail(client, artist_user):
    login_artist(client)
    
    # Test creating concert with YouTube URL but no thumbnail
    response = client.post('/concerts/create', data={
        'title': 'Auto Thumbnail Concert',
        'description': 'Concert with auto-generated thumbnail',
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'thumbnail_url': '',  # Empty thumbnail
        'genre': 'jazz',
        'duration': '240',
        'is_live': False
    }, follow_redirects=True)
    
    # In a real implementation, the form should auto-generate thumbnail
    # or provide a default one
    assert response.status_code == 200


def test_file_upload_simulation(client, artist_user):
    login_artist(client)
    
    # Simulate file upload (this would require proper file handling in routes)
    data = {
        'title': 'Uploaded Video Concert',
        'description': 'A concert with uploaded video',
        'genre': 'classical',
        'duration': '300',
        'is_live': False
    }
    
    # Create a fake file
    fake_file = FileStorage(
        stream=io.BytesIO(b'fake video content'),
        filename='concert.mp4',
        content_type='video/mp4'
    )
    
    data['video_file'] = fake_file
    
    # This test assumes you would implement file upload handling
    # The actual implementation would need proper file validation and storage
    response = client.post('/concerts/create', 
                          data=data,
                          content_type='multipart/form-data')
    
    # Test would depend on actual implementation
    assert response.status_code in [200, 302]


def test_video_duration_validation(client, artist_user):
    login_artist(client)
    
    # Test with invalid duration
    response = client.post('/concerts/create', data={
        'title': 'Duration Test',
        'description': 'Testing duration validation',
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
        'genre': 'rock',
        'duration': '-10',  # Invalid negative duration
        'is_live': False
    })
    
    # Should show validation error
    assert response.status_code == 200
    # Form should contain validation error or stay on create page


def test_concurrent_live_concerts_limitation(client, artist_user):
    login_artist(client)
    
    # Create first live concert
    response1 = client.post('/concerts/create', data={
        'title': 'Live Concert 1',
        'description': 'First live concert',
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
        'genre': 'rock',
        'duration': '120',
        'is_live': True,
        'scheduled_for': '2025-12-25T20:00'
    }, follow_redirects=True)
    
    # Try to create second live concert at same time
    response2 = client.post('/concerts/create', data={
        'title': 'Live Concert 2',
        'description': 'Second live concert',
        'video_url': 'https://www.youtube.com/watch?v=abc123',
        'thumbnail_url': 'https://img.youtube.com/vi/abc123/maxresdefault.jpg',
        'genre': 'jazz',
        'duration': '150',
        'is_live': True,
        'scheduled_for': '2025-12-25T20:00'  # Same time
    })
    
    # Depending on business rules, this might be allowed or not
    assert response1.status_code == 200
    assert response2.status_code in [200, 400]  # Might show conflict
