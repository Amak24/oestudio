from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, DateTimeField, FileField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional, ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_artist = BooleanField('Register as an Artist')
    submit = SubmitField('Register')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    profile_picture = StringField('Profile Picture URL', validators=[Optional(), URL()])
    submit = SubmitField('Update Profile')


class ConcertForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=256)])
    description = TextAreaField('Description', validators=[DataRequired()])
    video_url = StringField('Video URL', validators=[DataRequired(), URL()])
    thumbnail_url = StringField('Thumbnail URL', validators=[DataRequired(), URL()])
    genre = SelectField('Genre', choices=[
        ('', 'Select Genre'),
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('electronic', 'Electronic'),
        ('folk', 'Folk'),
        ('hip-hop', 'Hip Hop'),
        ('country', 'Country'),
        ('blues', 'Blues'),
        ('spiritual', 'Spiritual'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    duration = StringField('Duration (minutes)', validators=[Optional()])
    is_live = BooleanField('Live Concert')
    scheduled_for = DateTimeField('Scheduled For', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Create Concert')


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    concert_id = HiddenField('Concert ID', validators=[DataRequired()])
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    genre = SelectField('Genre', choices=[
        ('', 'All Genres'),
        ('rock', 'Rock'),
        ('pop', 'Pop'),
        ('jazz', 'Jazz'),
        ('classical', 'Classical'),
        ('electronic', 'Electronic'),
        ('folk', 'Folk'),
        ('hip-hop', 'Hip Hop'),
        ('country', 'Country'),
        ('blues', 'Blues'),
        ('spiritual', 'Spiritual'),
        ('other', 'Other')
    ], validators=[Optional()])
    is_live = BooleanField('Live Only')
    submit = SubmitField('Search')