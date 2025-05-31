import pytest
from forms import (
    LoginForm,
    RegistrationForm,
    ProfileForm,
    ConcertForm,
    CommentForm,
    SearchForm,
)
from datetime import datetime


def test_login_form_valid():
    form = LoginForm(data={"email": "user@example.com", "password": "secret"})
    assert form.validate() is True


def test_login_form_invalid_email():
    form = LoginForm(data={"email": "invalid", "password": "secret"})
    assert form.validate() is False


def test_registration_form_password_mismatch():
    form = RegistrationForm(data={
        "username": "user",
        "email": "user@example.com",
        "password": "password123",
        "confirm_password": "differentpass"
    })
    assert form.validate() is False


def test_profile_form_optional_fields():
    form = ProfileForm(data={
        "username": "testuser",
        "email": "test@example.com",
        "bio": "",
        "profile_picture": ""
    })
    assert form.validate() is True


def test_concert_form_valid():
    form = ConcertForm(data={
        "title": "Live Show",
        "description": "An amazing concert",
        "video_url": "http://example.com/video",
        "thumbnail_url": "http://example.com/thumb",
        "genre": "rock",
        "duration": "120",
        "is_live": True,
        "scheduled_for": "2025-12-25T20:00"
    })
    assert form.validate() is True


def test_concert_form_missing_url():
    form = ConcertForm(data={
        "title": "Missing URL",
        "description": "No URL",
        "video_url": "",
        "thumbnail_url": "",
        "genre": "rock",
        "duration": "90"
    })
    assert form.validate() is False


def test_comment_form_valid():
    form = CommentForm(data={
        "content": "Great show!",
        "concert_id": "123"
    })
    assert form.validate() is True


def test_comment_form_empty_content():
    form = CommentForm(data={
        "content": "",
        "concert_id": "123"
    })
    assert form.validate() is False


def test_search_form_empty():
    form = SearchForm(data={})
    assert form.validate() is True


def test_search_form_with_genre():
    form = SearchForm(data={"query": "Jazz Night", "genre": "jazz", "is_live": True})
    assert form.validate() is True
