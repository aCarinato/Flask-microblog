from datetime import datetime
from app import db      # import from __init__ the instance of SQLAlchemy(app)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin       # generic implementations of login that are appropriate for most user model classes
from app import login
from hashlib import md5

class User(UserMixin, db.Model):
    # fields are created as instances of the db.Column class
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic') # initialise the new post field for the User class
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        '''Generate a hash for the user's input password using werkzeug'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''check if a certain hash corresponds to a certain password'''
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # indexing allows to retrieve in chronological order
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'

# Flask-Login keeps track of the logged in user by storing its unique identifier in Flask's user session.
# Because Flask-Login knows nothing about databases, it needs the application's help in loading a user.
# That's why the extension expects that the application will configure a user loader function that can be called to load a user given the ID.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
