from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime


# this decorator can be used on any function we want to run before the view function
@app.before_request
def before_request():
    # when you reference current_user, Flask-Login invokes user loader that runs database query
    # so there will already be a db session running
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# route to index
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been submitted')
        return redirect(url_for('index'))

    # Uses our followed_posts() method to return a query of posts - all() triggers the execution of method
    posts = current_user.followed_posts().all()

    return render_template('index.html', title='Home', form=form, posts=posts)


# route to login page
# accept both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in, redirect to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # query the User database for the user matching the username in the form
        # .first() only gets the first result of the query since usernames are unique!
        user = User.query.filter_by(username=form.username.data).first()
        # if username is invalid or password check fails, flash error
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            # then redirect to login screen
            return redirect(url_for('login'))
        # if username and password check succeeds, login user (set user to current_user)
        login_user(user, remember=form.remember_me.data)
        # after user is logged in, determine which page to pass them to
        next_page = request.args.get('next')
        # if there is no next_page, user is redirected to index
        # url_parse checks that next_page is a relative location and not an absolute path
        # this prevents attackers from inserting a foreign URL
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # redirect user to next_page based on above logic
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# route to logout page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Route to registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# add view function for user profile pages
# the view function has a dynamic component as denoted by <username> so that Flask can fill in with logged in user
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Text post #1'},
        {'author': user, 'body': 'Text post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="Edit Profile", form=form)


# Route to a followed user
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found: ').format(username)
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You have unfollowed {}'.format(username))
    return redirect(url_for('user', username=username))
