from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import app, db
from models import User, Concert, Comment, Like
from forms import LoginForm, RegistrationForm, ProfileForm, ConcertForm, CommentForm, SearchForm


# Home route
@app.route('/')
def index():
    # Get upcoming live concerts
    upcoming_live = Concert.query.filter_by(is_live=True)\
        .filter(Concert.scheduled_for >= datetime.utcnow())\
        .order_by(Concert.scheduled_for)\
        .limit(6).all()
    
    # Get popular recorded concerts
    popular_recorded = db.session.query(Concert, db.func.count(Like.id).label('like_count'))\
        .outerjoin(Like)\
        .filter(Concert.is_live == False)\
        .group_by(Concert.id)\
        .order_by(db.desc('like_count'))\
        .limit(6).all()
    
    popular_recorded = [concert for concert, _ in popular_recorded]
    
    # Get featured concert (Ne-Yo demo or most popular)
    featured_concert = Concert.query.filter_by(title='Ne-Yo Live at NPR Music Tiny Desk Concert').first()
    
    # If Ne-Yo concert doesn't exist, create it
    if not featured_concert:
        neyo = User.query.filter_by(username='Ne-Yo').first()
        if not neyo:
            neyo = User(
                username='Ne-Yo',
                email='neyo@oestudio.com',
                is_artist=True,
                bio='Grammy Award-winning R&B singer, songwriter, and producer known for hits like "So Sick" and "Miss Independent".',
                profile_picture='https://i.ytimg.com/vi/vR6_ZVKEhJ4/maxresdefault.jpg'
            )
            neyo.set_password('neyo123')
            db.session.add(neyo)
            db.session.flush()
        
        featured_concert = Concert(
            title='Ne-Yo Live at NPR Music Tiny Desk Concert',
            artist_id=neyo.id,
            description='Experience Ne-Yo\'s incredible acoustic performance at NPR Music\'s Tiny Desk Concert. Watch as he performs stripped-down versions of his biggest hits in an intimate setting.',
            video_url='https://www.youtube.com/embed/vR6_ZVKEhJ4',
            thumbnail_url='https://i.ytimg.com/vi/vR6_ZVKEhJ4/maxresdefault.jpg',
            genre='R&B',
            duration=1200,  # 20 minutes
            is_live=False
        )
        db.session.add(featured_concert)
        db.session.commit()
    
    # Fallback to most popular if still no featured concert
    if not featured_concert and popular_recorded:
        featured_concert = popular_recorded[0]
    
    return render_template('index.html', 
                          upcoming_live=upcoming_live,
                          popular_recorded=popular_recorded,
                          featured_concert=featured_concert,
                          datetime=datetime,
                          now=datetime.utcnow(),
                          title="O Estúdio - Live Concert Streaming")


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('profile'))
    
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Username already exists. Please choose a different one.', 'danger')
            else:
                flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        try:
            user = User(username=form.username.data, 
                       email=form.email.data,
                       is_artist=form.is_artist.data)
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Congratulations, you are now registered!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# User profile routes
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile', user=current_user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.profile_picture.data = current_user.profile_picture
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        if form.profile_picture.data:
            current_user.profile_picture = form.profile_picture.data
        
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', title='Edit Profile', form=form, editing=True)


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    concerts = []
    
    if user.is_artist:
        concerts = Concert.query.filter_by(artist_id=user.id).order_by(Concert.created_at.desc()).all()
    
    return render_template('profile.html', title=f"{user.username}'s Profile", user=user, concerts=concerts)


# Concert routes
@app.route('/concerts')
def concerts():
    form = SearchForm(request.args)
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Concert.query
    
    # Apply filters
    if form.query.data:
        search = f"%{form.query.data}%"
        query = query.filter(
            (Concert.title.like(search)) | 
            (Concert.description.like(search))
        )
    
    if form.genre.data:
        query = query.filter_by(genre=form.genre.data)
    
    if form.is_live.data:
        query = query.filter_by(is_live=True)
    
    # Order by most recent
    concerts = query.order_by(Concert.created_at.desc()).paginate(page=page, per_page=12)
    
    return render_template('search.html', title='Browse Concerts', concerts=concerts, form=form, now=datetime.utcnow())


@app.route('/concert/<int:concert_id>')
def concert(concert_id):
    concert = Concert.query.get_or_404(concert_id)
    comments = Comment.query.filter_by(concert_id=concert_id).order_by(Comment.created_at.desc()).all()
    comment_form = CommentForm()
    comment_form.concert_id.data = concert_id
    
    # Check if the current user has liked this concert
    user_like = None
    if current_user.is_authenticated:
        user_like = Like.query.filter_by(user_id=current_user.id, concert_id=concert_id).first()
    
    # Get similar concerts
    similar_concerts = Concert.query.filter(
        (Concert.genre == concert.genre) & 
        (Concert.id != concert.id)
    ).limit(4).all()
    
    like_count = Like.query.filter_by(concert_id=concert_id).count()
    
    return render_template('concert.html', 
                          title=concert.title,
                          concert=concert, 
                          comments=comments,
                          comment_form=comment_form,
                          user_like=user_like,
                          like_count=like_count,
                          now=datetime.utcnow(),
                          similar_concerts=similar_concerts)


@app.route('/concert/create', methods=['GET', 'POST'])
@login_required
def create_concert():
    if not current_user.is_artist and not current_user.is_admin:
        flash('Only artists can create concerts', 'danger')
        return redirect(url_for('index'))
    
    form = ConcertForm()
    if form.validate_on_submit():
        # Convert duration from minutes to seconds
        try:
            duration_seconds = int(float(form.duration.data) * 60)
        except ValueError:
            duration_seconds = 0
        
        concert = Concert(
            title=form.title.data,
            artist_id=current_user.id,
            description=form.description.data,
            video_url=form.video_url.data,
            thumbnail_url=form.thumbnail_url.data,
            genre=form.genre.data,
            duration=duration_seconds,
            is_live=form.is_live.data,
            scheduled_for=form.scheduled_for.data if form.is_live.data else None
        )
        
        db.session.add(concert)
        db.session.commit()
        
        flash('Your concert has been created!', 'success')
        return redirect(url_for('concert', concert_id=concert.id))
    
    return render_template('artist_dashboard.html', title='Create Concert', form=form)


@app.route('/concert/<int:concert_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_concert(concert_id):
    concert = Concert.query.get_or_404(concert_id)
    
    # Check if the current user is the artist or an admin
    if not (current_user.id == concert.artist_id or current_user.is_admin):
        flash('You do not have permission to edit this concert', 'danger')
        return redirect(url_for('concert', concert_id=concert_id))
    
    form = ConcertForm()
    
    if request.method == 'GET':
        form.title.data = concert.title
        form.description.data = concert.description
        form.video_url.data = concert.video_url
        form.thumbnail_url.data = concert.thumbnail_url
        form.genre.data = concert.genre
        form.duration.data = str(concert.duration / 60) if concert.duration else ""
        form.is_live.data = concert.is_live
        form.scheduled_for.data = concert.scheduled_for
    
    if form.validate_on_submit():
        # Convert duration from minutes to seconds
        try:
            duration_seconds = int(float(form.duration.data) * 60)
        except ValueError:
            duration_seconds = 0
            
        concert.title = form.title.data
        concert.description = form.description.data
        concert.video_url = form.video_url.data
        concert.thumbnail_url = form.thumbnail_url.data
        concert.genre = form.genre.data
        concert.duration = duration_seconds
        concert.is_live = form.is_live.data
        concert.scheduled_for = form.scheduled_for.data if form.is_live.data else None
        
        db.session.commit()
        flash('Concert details have been updated!', 'success')
        return redirect(url_for('concert', concert_id=concert_id))
    
    return render_template('artist_dashboard.html', title='Edit Concert', form=form, editing=True)


@app.route('/concert/<int:concert_id>/delete', methods=['POST'])
@login_required
def delete_concert(concert_id):
    concert = Concert.query.get_or_404(concert_id)
    
    # Check if the current user is the artist or an admin
    if not (current_user.id == concert.artist_id or current_user.is_admin):
        flash('You do not have permission to delete this concert', 'danger')
        return redirect(url_for('concert', concert_id=concert_id))
    
    db.session.delete(concert)
    db.session.commit()
    
    flash('Concert has been deleted', 'success')
    return redirect(url_for('index'))


# Comment routes
@app.route('/comment/add', methods=['POST'])
@login_required
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        concert = Concert.query.get_or_404(form.concert_id.data)
        
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            concert_id=concert.id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Your comment has been added!', 'success')
        
        # If it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'id': comment.id,
                'content': comment.content,
                'author': current_user.username,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
    
    return redirect(url_for('concert', concert_id=form.concert_id.data))


@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author or an admin
    if not (current_user.id == comment.user_id or current_user.is_admin):
        flash('You do not have permission to delete this comment', 'danger')
        return redirect(url_for('concert', concert_id=comment.concert_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment has been deleted', 'success')
    
    # If it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    return redirect(url_for('concert', concert_id=comment.concert_id))


# Like routes
@app.route('/concert/<int:concert_id>/like', methods=['POST'])
@login_required
def like_concert(concert_id):
    concert = Concert.query.get_or_404(concert_id)
    
    # Check if the user already liked this concert
    existing_like = Like.query.filter_by(user_id=current_user.id, concert_id=concert_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        like = Like(user_id=current_user.id, concert_id=concert_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    
    like_count = Like.query.filter_by(concert_id=concert_id).count()
    
    # If it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'liked': liked,
            'count': like_count
        })
    
    return redirect(url_for('concert', concert_id=concert_id))


# Artist dashboard
@app.route('/artist/dashboard')
@login_required
def artist_dashboard():
    if not current_user.is_artist and not current_user.is_admin:
        flash('You do not have access to the artist dashboard', 'danger')
        return redirect(url_for('index'))
    
    # Get all concerts by the artist
    concerts = Concert.query.filter_by(artist_id=current_user.id).order_by(Concert.created_at.desc()).all()
    
    return render_template('artist_dashboard.html', title='Artist Dashboard', concerts=concerts, now=datetime.utcnow())


# Admin panel
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('You do not have access to the admin panel', 'danger')
        return redirect(url_for('index'))
    
    # Get all users
    users = User.query.all()
    
    # Get all concerts
    concerts = Concert.query.order_by(Concert.created_at.desc()).all()
    
    return render_template('admin_panel.html', title='Admin Panel', users=users, concerts=concerts, now=datetime.utcnow())


@app.route('/admin/toggle_artist/<int:user_id>', methods=['POST'])
@login_required
def toggle_artist(user_id):
    if not current_user.is_admin:
        flash('You do not have permission', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    user.is_artist = not user.is_artist
    db.session.commit()
    
    flash(f'Artist status for {user.username} has been updated', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('You do not have permission', 'danger')
        return redirect(url_for('index'))
    
    # Prevent removing admin status from self
    if user_id == current_user.id:
        flash('You cannot remove your own admin status', 'danger')
        return redirect(url_for('admin_panel'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Admin status for {user.username} has been updated', 'success')
    return redirect(url_for('admin_panel'))


# API Routes for React Frontend
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username}})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        is_artist=data.get('is_artist', False)
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User registered successfully'})

@app.route('/api/concerts', methods=['GET'])
def api_concerts():
    concerts = Concert.query.order_by(Concert.created_at.desc()).all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'artist': c.artist.username,
        'genre': c.genre,
        'thumbnail_url': c.thumbnail_url,
        'is_live': c.is_live
    } for c in concerts])

@app.route('/api/concert/create', methods=['POST'])
@login_required
def api_create_concert():
    data = request.get_json()
    if not current_user.is_artist:
        return jsonify({'success': False, 'message': 'Only artists can create concerts'}), 403
    
    duration_seconds = int(float(data.get('duration', 0)) * 60)
    concert = Concert(
        title=data.get('title'),
        artist_id=current_user.id,
        description=data.get('description'),
        video_url=data.get('video_url'),
        thumbnail_url=data.get('thumbnail_url'),
        genre=data.get('genre'),
        duration=duration_seconds,
        is_live=data.get('is_live', False),
        scheduled_for=datetime.fromisoformat(data.get('scheduled_for')) if data.get('scheduled_for') else None
    )
    db.session.add(concert)
    db.session.commit()
    return jsonify({'success': True, 'concert_id': concert.id})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500


# Seed admin user
@app.route('/seed_admin', methods=['GET'])
def seed_admin():
    # Check if admin already exists
    admin = User.query.filter_by(email='admin@oestudio.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@oestudio.com',
            is_artist=True,
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return "Admin user created!"
    return "Admin user already exists!"


# Seed demo data including Ne-Yo video
@app.route('/seed_demo', methods=['GET'])
def seed_demo():
    # Create Ne-Yo artist if doesn't exist
    neyo = User.query.filter_by(username='Ne-Yo').first()
    if not neyo:
        neyo = User(
            username='Ne-Yo',
            email='neyo@oestudio.com',
            is_artist=True,
            bio='Grammy Award-winning R&B singer, songwriter, and producer known for hits like "So Sick" and "Miss Independent".',
            profile_picture='https://i.ytimg.com/vi/vR6_ZVKEhJ4/maxresdefault.jpg'
        )
        neyo.set_password('neyo123')
        db.session.add(neyo)
        db.session.flush()  # Get the ID
    
    # Check if demo concert already exists
    demo_concert = Concert.query.filter_by(title='Ne-Yo Live at NPR Music Tiny Desk Concert').first()
    if not demo_concert:
        demo_concert = Concert(
            title='Ne-Yo Live at NPR Music Tiny Desk Concert',
            artist_id=neyo.id,
            description='Experience Ne-Yo\'s incredible acoustic performance at NPR Music\'s Tiny Desk Concert. Watch as he performs stripped-down versions of his biggest hits in an intimate setting.',
            video_url='https://www.youtube.com/embed/vR6_ZVKEhJ4',
            thumbnail_url='https://i.ytimg.com/vi/vR6_ZVKEhJ4/maxresdefault.jpg',
            genre='R&B',
            duration=1200,  # 20 minutes
            is_live=False
        )
        db.session.add(demo_concert)
    
    db.session.commit()
    return "Demo data seeded successfully!"
