from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import Users
from flask_babel import lazy_gettext as _l

        
class EditProfileForm(FlaskForm):
    """form allows user to edit his personal profile info"""
    
    username  = StringField  (_l('Username'), validators=[DataRequired()]) 
    about_me  = TextAreaField(_l('About me'), validators=[Length(min=0, max=150)])
    submit    = SubmitField  (_l('Edit'))

    def __init__(self, original_username, *args, **kwargs): # the original_username must be passed from the view function 
        super (EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username  # creates a new var with the orignal name of the user

    def validate_username(self, username):
        """custom validator, check if the username chosen is already in use and raises an error

        :param username: new chosen username
        :type username: str
        :raises ValidationError: error
        """
        if username.data != self.original_username:
            user = Users.query.filter_by(username = self.username.data).first()   # search in the db if there are other users with the same username
            if user is not None:
                raise ValidationError(_l('Please choose another user'))  # if there are other users with the chosen username, raise an error

class EmptyForm(FlaskForm):
    """allows to generate a form with only a button, so you can integrate it as a POST request and send data without make them appear in the url like a GET"""
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    """Form allows to add posts"""
    post   = TextAreaField(_l('say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
