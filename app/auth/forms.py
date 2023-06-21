from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import Users
from flask_babel import lazy_gettext as _l


class LoginForm(FlaskForm):
    username    = StringField  (_l('Username'), validators=[DataRequired(),Length(min=0, max=64)])
    password    = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField (_l('Remember me'))
    submit      = SubmitField  (_l('sign in'))

class RegistrationForm(FlaskForm):
    username  = StringField  (_l('Username'),         validators=[DataRequired(), Length(min=0, max=64)])
    email     = EmailField   (_l('email'),            validators=[DataRequired(), Email(), Length(min=0, max=64)])
    password  = PasswordField(_l('Password'),         validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit    = SubmitField  (_l('Register now'))
    
    # custom validators named "validate_<name_field>" are automaticcaly called by WTForms ad validators in the respective field
    def validate_username(self, username):
        """ search for another user with the same username in the db """
        user = Users.query.filter_by(username= username.data).first()
        if user is not None:
            raise ValidationError(_l('username already exixts'))  
        
    def validate_email(self, email):
        """ search for another user with the same email in the db """
        user = Users.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError(_l('email already used'))

class ResetPasswordRequestForm(FlaskForm):
     """form that send a reset password request -> wll be sent via email """
     email  = EmailField(_l('email'), validators=[DataRequired(), Email(), Length(min=0, max=64)])
     submit = SubmitField(_l('Request Password restet'))

class ResetPasswordForm(FlaskForm):
    """form to actually reset the password"""
    password  = PasswordField(_l('New Password'),     validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit    = SubmitField  (_l('change password'))