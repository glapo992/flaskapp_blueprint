from flask import render_template
from app import db
from app.errors import bp


# is a normal view like those on routes
#@app.errorhandler(404)   # old decorator, if hte funct is used outside a blueprint
@bp.app_errorhandler(404) # new decorator if the function is used with blueprint
def not_found_errro(error):
    return render_template('404.html', title = 'error 404'), 404  # returns also a status code of the error 



@bp.app_errorhandler(500)
def internal_errro(error):
    # To make sure any failed database sessions do not interfere with any database accesses triggered by the template, a session rollback is issued. 
    # This resets the session to a clean state.
    db.session.rollback()  
    return render_template('500.html', title = 'error 500'), 500