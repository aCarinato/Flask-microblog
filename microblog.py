from app import app, db, cli     # import the app variable (Flask instance) which is member of the app package
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'User':User, 'Post':Post}
