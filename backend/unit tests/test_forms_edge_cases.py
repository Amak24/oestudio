import pytest
from forms import (
    LoginForm,
    RegistrationForm,
    ProfileForm,
    ConcertForm,
    CommentForm,
    SearchForm
)


def test_login_form_missing_fields():
    form = LoginForm(data={})
    assert form.validate() is False
    assert "email" in form.errors
    assert "password" in form.errors


def test_registration_form_username_too_short():
    form = RegistrationForm(data={
        "username": "ab",
        "email": "valid@example.com",
        "password": "12345678",
        "confirm_password": "12345678"
    })
    assert form.validate() is False
    assert "username" in form.errors


def test_registration_form_password_too_short():
    form = RegistrationForm(data={
        "username": "validuser",
        "email": "valid@example.com",
        "password": "short",
        "confirm_password": "short"
    })
    assert form.validate() is False
    assert "password" in form.errors


def test_profile_form_bio_too_long():
    form = ProfileForm(data={
        "username": "validuser",
        "email": "user@example.com",
        "bio": "a" * 501  # 1 character over the limit
    })
    assert form.validate() is False
    assert "bio" in form.errors


def test_profile_form_invalid_url():
    form = ProfileForm(data={
        "username": "validuser",
        "email": "user@example.com",
        "profile_picture": "not_a_url"
    })
    assert form.validate() is False
    assert "profile_picture" in form.errors


def test_concert_form_invalid_urls():
    form = ConcertForm(data={
        "title": "Concert",
        "description": "Fun time",
        "video_url": "invalid_url",
        "thumbnail_url": "also_invalid",
        "genre": "rock",
        "duration": "90"
    })
    assert form.validate() is False
    assert "video_url" in form.errors
    assert "thumbnail_url" in form.errors


def test_comment_form_missing_concert_id():
    form = CommentForm(data={
        "content": "This was awesome!"
    })
    assert form.validate() is False
    assert "concert_id" in form.errors


def test_search_form_invalid_genre_choice():
    form = SearchForm(data={"genre": "metal"})
    assert form.validate() is False  # "metal" is not in the defined choices
