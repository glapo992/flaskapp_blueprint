import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # flask general vars
    FLASK_ENV   = os.environ.get('FLASK_ENV')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')
    SECRET_KEY  = os.environ.get('SECRET_KEY')

    # database settings
    if os.environ.get('DB_HOST'):
        DB_USERNAME = os.environ.get('DB_USERNAME') 
        DB_PASSWORD = os.environ.get('DB_PASSWORD') 
        DB_HOST     = os.environ.get('DB_HOST') 
        DB_NAME     = os.environ.get('DB_DB_NAME') 

        if DB_USERNAME and DB_PASSWORD and DB_HOST and DB_NAME:
            db_url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        else:
            raise KeyError('Some necessary environment variable(s) are not defined')
        SQLALCHEMY_DATABASE_URI = db_url
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'+ os.path.join(basedir, 'app.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
   
    # mail server 
    MAIL_SERVER                    = os.environ.get('MAIL_SERVER')
    MAIL_PORT                      = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS                   = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME                  = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD                  = os.environ.get('MAIL_PASSWORD')
    ADMINS                         = ['your-email@example.com']

    # Pagination configs
    POST_PER_PAGE = 10 

    # language support
    # list of supported languages codes for Babel extension
    LANGUAGES = ['en','it']