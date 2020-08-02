from datetime import datetime
from app import db      # import from __init__ the instance of SQLAlchemy(app)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin       # generic implementations of login that are appropriate for most user model classes
from app import login
from hashlib import md5
from time import time
import jwt
from app import app

# the following table is not declared as a model, like users and posts tables.
# this is an auxiliary table that has no other data than the foreign keys
# It is used to create the many-to-many relationship in the user table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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

    # The setup of many-to-many relationship is not trivial: db.relationship function is used to define it in the model class.
    # This relation links User instances to other User instances
    followed = db.relationship(
        'User',                                             # right-side entity of the relationship (the left side is the parent class)
        secondary=followers,                                # configures the association table
        primaryjoin = (followers.c.follower_id == id),      # indicates the condiion tht links the left side entity with the association table
        secondaryjoin = (followers.c.followed_id == id),    # indicates the condiion tht links the right side entity with the association table
        backref = db.backref('followers', lazy='dynamic'),  # how the relationship will be accessed from the right side entity
        lazy='dynamic')                                     # similar to above but applied to the left side query

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        # issues a query on the followed relationship to check if a link between two users already exists
        # Looks for items in the association table that have the left side foreign key set to the self user and the right to the user argument
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0 # the number can either be 0 or 1

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)                 # posts of the followed users
        own = Post.query.filter_by(user_id=self.id)                 # own post, as if one is a follower of himself
        return followed.union(own).order_by(Post.timestamp.desc())  # merging the two above so the own posts are also displayed

    def get_reset_password_token(self, expires_in=600):
        """
        Function to regenerate password from reset token.
        If a tken has a valid signature but it is past its expiration timestamp, it will considered invalid (10 minutes).
        When the user clicks on the emailed link, the token is going to be sent back to the application as part of the URL and the firt thing the view function That
        handles this URL will do is to verify it.
        I f the signature is valid, then the user can be verified by the ID stored in the payload.

        OUTPUT:
            - generates JWT token as a string
        """
        return jwt.encode(
        {'reset_password': self.id, 'exp': time() + expires_in},
        app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    # a static method can be invoked directly from the class.
    # It is similar to a class method with the difference that it does not receive the class as a first argument.
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:         # the token cannot be avlidated or is expired
            return
        return User.query.get(id) # the value of the reset_password key from the token's paylod is the ID of the user, so the user can be loaded and return

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
