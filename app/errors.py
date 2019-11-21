"""
Routes for error pages

Works similarly to view functions. The normal view functions don't need to be passed a second return value to
render_template because we wanted them to have the default return value, which is 200 success.
"""

from flask import render_template
from app import app, db

# 404 error handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# 500 error handler
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
