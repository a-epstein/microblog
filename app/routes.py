from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user
from app import app
from app.forms import LoginForm
from app.models import User

# route to index
@app.route('/')
@app.route('/index')
def index():
    """
    :return: render template with our HTML
    :rtype: render_template
    """
    user = {'username': 'Amanda'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user,posts=posts)

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
        # then redirect to index
        return redirect(url_for('index'))
    return render_template('login.html',title='Sign In', form=form)