# routes are the different URLs that the application implements
# handlers for the application routes are written as python functions, called view functions
from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import User
from app import db
from datetime import datetime

# The way Flask-Login protects a view function against anonymous users is with a decorator called @login_required
# When this is added to a view function below the @app.route the function becomes protected and will not allow access to non-authenticated users
@app.route('/')         # creates an assocition between the URL given as an argument and the funciton
@app.route('/index')    # when the browser requests either '/' or '/index' flask is going to invoke index()
@login_required
def index():
    user = {'username':'Ale'}
    posts = [
    {
        'author': {'username':'Jo'},
        'body': 'nice day here'
    },
    {
        'author': {'username':'susy'},
        'body': 'cool'
    }
    ]

    return render_template('index.html', title='Home Page', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
# GET requests are those that return information to the client (web browser in this case)
# POST requests are typically used when the browser submits form data to the server
def login():
    # the following lines deal with this situation:
    # a user is logged-in and navigates to the /login URL of the application: this is a mistake and needs to be avoided
    #
    if current_user.is_authenticated:   # current_user is a variable that comes with Flask-Login -> obtain the user object that represent the client of the request        return redirect(url_for('index'))
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():   # this does all the form processig work
        # query the database to find the user
        user = User.query.filter_by(username=form.username.data).first() # the result is a query that only includes the objects that have a matching username
        # since there are only 0 or 1 results the query is completed by calling first()

        if user is None or not user.check_password(form.password.data): # take the password hash stored with the user and determine if the password entered in the form matches the hash
            # when the browser sends POST request as a result of user pressing button this is going to return True if everything is OK
            flash('Invalid username or password')
            # either username or password was wrong, then redirect to the login prompt
            return redirect(url_for('login'))

        # if username and passwd are both correct the login_user() will register the user as logged in:
        # any future pages the user navigates to will have the current_user variable set to that user
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')        # request variable contains all the information that the client sent with the request
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))


    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # creates a new user with the username, email and password provided, writes it to the database and redirects to the login propmpt
        # so that the user can log in
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

# To create a user profile page a view function that maps to the /user/<username>URL is needed
@app.route('/user/<username>')  # this decorator has a dynamic component in it i.e. <username>
@login_required                 # this makes this view function only accessible to logged in users
def user(username):
    user = User.query.filter_by(username=username).first_or_404()   # load the user from the database
    posts = [
        {'author': user, 'body':'Test post #1'},
        {'author': user, 'body':'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

# check if the current_user is logged in  and in that case sets the last_seen field to the current time
@app.before_request         # registers the decorated function to be executed right before the view function
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        # copy the data from the form into the user object and then write the object to the database
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)
