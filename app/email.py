from flask import current_app
from flask_mail import Message
from app import mail

from threading import Thread


def send_async_email (app, msg):
    """make the email function to work in background in async
    send also app istance and create app context()
    allows the mail extension to find Falsl app istance 
    mail.send() has to access the config value that are related to the current app istace"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body:str, html_body):
    """allows to send emails to a user

    :param subject: the subject of the email 
    :type subject: str
    :param sender: sender of the email
    :type sender: str
    :param recipients: destination mail addr  
    :type recipients: str
    :param text_body: text body of the email
    :type text_body: str
    :param html_body: html body of the email
    :type html_body: str html
    """
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # enable multithread to send email async, get_current_object is the real application istance
    # here the app is passed as arg to a background thread.
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

