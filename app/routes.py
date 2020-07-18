# routes are the different URLs that the application implements
# handlers for the application routes are written as python functions, called view functions
from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app.models import User
from app import db

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
