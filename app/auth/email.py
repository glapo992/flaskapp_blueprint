# actually send the email
from flask import render_template
from app import current_app

from app.email import send_email

def send_password_reset_email(user):
    """send an email to the user when the password reset is requested, it uses a token to validate the request

    :param user: the user who requested the pw reset
    :type user: Users
    """
    token = user.get_reset_password_token() # 
    send_email('reset password',
                sender=current_app.config['ADMINS'][0],
                recipients=[user.email], 
                text_body=render_template('email_templates/reset_pwd.txt', user = user, token = token),    
                html_body=render_template('email_templates/reset_pwd.html', user = user, token = token))   