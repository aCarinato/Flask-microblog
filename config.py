import os
basedir = os.path.abspath(os.path.dirname(__file__)) # main directory of the application. It is used to store app.db

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Flask-SQLAlchemy extension takes the location of the application's database from the SQLALCHEMY_DATABASE_URI conf. var.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # the database URL is taken from the DATABASE_URL env. var., and if it is not defined a db name app.db is configured in the main directory of the app

    SQLALCHEMY_TRACK_MODIFICATIONS = False # it's an unnecessary feature that is therefore disabled

    # the below is enable email sending when an error occurs
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['alessandro.carinato@gmail.com']

    POSTS_PER_PAGE = 3
    LANGUAGES = ['en', 'es']    # languages for translation

    MS_TRANSLATOR_KEY = 'e32d1bf3f3c9463c94c7d8af5655b5e9' # os.environ.get('MS_TRANSLATOR_KEY')
