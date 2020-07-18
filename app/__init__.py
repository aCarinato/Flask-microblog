from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate           # database migration engine
from flask_login import LoginManager        # managing user logged-in state

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)                        # database instance
migrate = Migrate(app, db)
login = LoginManager(app)
# Flask-Login needs to know what is the view function that handles logins
login.login_view = 'login' # 'login' is the function (or endpoint) name for the login view i.e. the nam one would use in a url_for() call

# the import at bottom is a workaround to circular imports
from app import routes, models      	   # 'models' define the structure of the database
