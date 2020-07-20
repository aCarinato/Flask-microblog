from flask import render_template
from app import app, db

# when things work in the view functions returns 200 (status code for a successful response)
# In this case these are error pages, so the status code of the response to reflect that is wanted 

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
