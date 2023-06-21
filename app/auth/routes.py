# login/registration imports
from app import db # from app module import app obj (is a Flask obj)
from flask import flash, redirect, render_template, request, url_for
from app.models import Users
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from flask_babel import _
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email
from app.auth import bp

# -----------------------AUTENTICATION VIEWS----------------------------



@bp.route('/login', methods=['GET', 'POST']) # this method accepts also post requests, as specified in the html from 
def login():
    """ this view manage the login function 
    the login library has required items that can be used 
    - is_authenticated: a property that is True if the user has valid credentials or False otherwise.
    - is_active: a property that is True if the user's account is active or False otherwise.
    - is_anonymous: a property that is False for regular users, and True for a special, anonymous user.
    - get_id(): a method that returns a unique identifier for the user as a string (unicode, if using Python)
    """
    if current_user.is_authenticated:
        return redirect (url_for('blog.index'))                      #  if the user is already auth, just return the index
     
    form = LoginForm()
    if form.validate_on_submit():                               # procss the form, returns true or false depending on the validators. if false require an error handler
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('invalid username or pw'))                     # must be handled in html. did in base.html so all pages can handle flash messages
            return redirect(url_for('auth.login'))                   # redirect with the url_for method
        login_user(user=user, remember=form.remember_me.data)   #flask function register the user as logged in. sets a variable current_user with the logged one for the duration of the session
        next_page = request.args.get('next')                    # the argument of the request -> is the url to the page the user want to visit, caught by @login_required (.../login?next=%2Ffeed)
        
        if not next_page or url_parse(next_page).netloc != "":  
            # ensure that the next is on the same site 
            #(an attacker could insert a different url in the ?next and have the login token to acceed also if is on another site). 
            #to determne if the url is relative or not, the netloc comonent must exixt
            next_page = (url_for('blog.index'))  # if next page does not exist, the url for index is assigned
        return redirect (next_page)

    return render_template ('login.html', form = form, title = _('Sign In'))

@bp.route('/logout')
def logout():
    """logs out the already logged user """
    logout_user()
    return redirect(url_for('blog.index'))

@bp.route('/registration', methods=['GET', 'POST']) # this method accepts also post requests, as specified in the html from 
def registration():
    """ new user registration view """
    if current_user.is_authenticated:
        return redirect (url_for('blog.index'))    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('registration ok'))
        return redirect(url_for('auth.login'))
    return render_template('registration.html', form = form , title= _('Registration'))   


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """this method allows to send an email with the reset password request"""
    if current_user.is_authenticated: # check if the user is already logged, in case of error
        return redirect (url_for('blog.index'))
    
    form = ResetPasswordRequestForm() 
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first() # search for the user with the given email
        if user:
            send_password_reset_email(user)
            flash (_("check your inbox"))
            return redirect (url_for('auth.login'))
    return render_template('reset_passwd_req.html', title = 'reset password', form = form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """display the reset password form and allows to change password

    :param token: the token sent via email
    :type: jwt token
    """
    if current_user.is_authenticated: # check if the user is already logged, in case of error
        print('Debug:user auth')
        return redirect (url_for('blog.index'))
    user = Users.verify_reset_password_token(token=token) # istance of the correct user 
    if not user:
        print('Debug:user not found')
        return redirect (url_for('blog.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("password changed"))
        return redirect (url_for('auth.login'))
    return render_template ('reset_password.html', form = form)

#----------------------------------------------------------------------------------------
