from flask import Flask, current_app
from config import Config


# DATABASE
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2 # just for future db connection with postgres
# to initialize a new db run on the terminal 'flask db init', it will create the migration engine 
try:
    db = SQLAlchemy()   
    migrate = Migrate() 

except psycopg2.DatabaseError as exeption:
    print ('database connection error')
    raise exeption 

#language supp
from flask_babel import Babel, _, lazy_gettext as _l
from flask import request
babel = Babel()


# Login
from flask_login import LoginManager 
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please, log in to access this page')

#log erors
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

#email support
from flask_mail import Mail
mail = Mail()

#bootstrap
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap() 

# Timezone 
from flask_moment import Moment
moment = Moment()

#language supp
from flask_babel import Babel, _, lazy_gettext as _l
from flask import request
babel = Babel()



def create_app(config_class = Config):
    """creation of the app istance. Allows the use of custom configuration for each istance

    :param config_class: the config for the app istance, defaults to Config
    :type config_class: Config, optional
    """
    app = Flask(__name__)
    app.config.from_object(config_class) # import configs from the Class Config in the as-named module. the values are accessed with a dict-like statement (app.config['SECRET_KEY'])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    bootstrap.init_app(app)

    #BLUEPRINT CONFIG------------------------------

    from app.errors import bp as errors_bp # import bp (as named in its module and set alias to specify that is the error bp. same workflow with other blueprints)
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth') # prefix is optional, add to all the bp routes this prefix

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp) 
   
    from app.translation import bp as translation_bp
    app.register_blueprint(translation_bp) 

    #-----------------------------------

    #LOG ERRORS TO EMAIL------------------------------
    if not app.debug and not app.testing:  
        if app.config['MAIL_SERVER']:   
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:  
                auth = (app.config['MAIL_USERNAME'], 
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            #istance of the handler which sends email and its configuration
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'],
                          app.config['MAIL_PORT']), 
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], 
                subject='application error',
                credentials=auth, secure=secure) 
            
            mail_handler.setLevel(logging.ERROR)  # level of the log reported (DEBUG, INFO, WARNING, ERROR, CRITICAL)

            app.logger.addHandler(mail_handler)
    #LOG ERRORS TO A FILE------------------------------
    if not app.debug and not app.testing: 
        if not os.path.exists('logs'):  # if the specified path of the folder doesnt exists, it is created now
            os.mkdir('logs')
        
        file_Handler = RotatingFileHandler('logs/blog.log', maxBytes=10240, backupCount=10)  

        file_Handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_Handler.setLevel(logging.INFO) # level of the log reported (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        app.logger.addHandler(file_Handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('application startup')
        
    return app


@babel.localeselector
def get_locale():
    """ fetch the lang settings of the client who made the request"""
    #return 'en' #forces to display the given lang
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from app import models