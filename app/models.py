# gneral imports
from app import db
from datetime import datetime 

# login stuff
from flask_login import UserMixin # generic login implementations suitable for most user model classes
from app import login

# pw hashing-> already provided in flask
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5 # optional, just for Gravatar service for avatar images

# token generation for pw reset request
import jwt 
from time import time

from flask import current_app


""" after a modificaion in the models, the migrate class will generate a script with the database version. 
run commands in the terminal:
flask db migrate -m <optional comments> --> creates the script that update the db with modifications on models (sort of git)
flask db upgrade --> applies the script to the database
flask db downgrade --> retunrs to a previous version of the db 

to add a record in the terminal:
python3
>>> from app import app, db
>>> from app.models import User, Posts
>>> app.app_context().push()      # allows sqlalchemy to acceed the ap.config without give app as argument
>>> u = Users(username='jj', email='jj@bravo.it')
>>> db.session.add(u)
>>> db.session.commit()  # write the data in the database

"""


# this table is not in a model -- aux table with foreign keys from another table 
# is a circular reference, where a user has a relation with another user (follow-follow)
# since is used by user class, must be declaed beofre it
followers = db.Table('followers', 
                     db.Column('follower_id', db.Integer, db.ForeignKey('users.id')), # foriegn_key
                     db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))  # foriegn_key
                     )


class Users(UserMixin ,db.Model): # added UserMixin at the user class
    """ some of the user already created for testing:
    username:pw
    - dr:pw
    """
    id        = db.Column      (db.Integer, primary_key = True)
    username  = db.Column      (db.String(64), index = True, unique = True)
    email     = db.Column      (db.String(64), index = True, unique = True)
    pw_hash   = db.Column      (db.String(128))
    posts     = db.relationship('Posts', backref = 'author', lazy = 'dynamic') # reference to the post Model class(not table name!!), is not a db field but a view of the realtionship
    about_me  = db.Column      (db.String(150))
    last_seen = db.Column      (db.DateTime, default = datetime.utcnow)
    followed  = db.relationship('Users', secondary = followers,   # db.relationshp defines a relation between tables. here is used to link User to another User (self refered). in this table left User follows the right User 
                                primaryjoin=(followers.c.follower_id == id),    # condition that links the left side entity (the follower user) with the association table -- follower_id is the column of the association table.
                                secondaryjoin=(followers.c.followed_id == id),  # like the primaryjoin, but now is used followed -> followers 
                                backref = db.backref('followers', lazy = 'dynamic'),lazy = 'dynamic')  # backref defines how this relationship will be accessed from the right side entity
 
    # hashing password--------------
    def set_password(self, password:str)->str:
        """generates a hash for the given pw and set it as param of the class

        :param password: hash
        :type password: str
        """
        self.pw_hash = generate_password_hash(password=password)

    def check_password(self, password:str)->bool:
        """check if the given password's hash is the same of the saved one

        :param password: passwd to check
        :type password: str
        :return: result of check
        :rtype: bool
        """
        return check_password_hash(self.pw_hash, password=password)
    
    # followers managing---------------------
    def is_following(self, user)->int:
        """ queries the followed relationship and search a link between the users"""
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0 # count method returns the number of results
    
    def follow(self, user)->None:
        """ add a user to the relationship table of the current user"""
        if not self.is_following(user):
            self.followed.append(user) #append add a new record on the table

    def unfollow(self, user)->None:
        """ remove a user from the table of the current user"""
        if  self.is_following(user):
            self.followed.remove(user) # remove an existing record

    def followed_posts(self):
        """ search and order all the posts of all followers of the current user, and his owns"""
        # first query search posts of followed people
        followed = Posts.query.join(followers,                                          # joins Posts and follower table with the condition followed_id == Posts.user_id)
                                 (followers.c.followed_id == Posts.user_id)).filter(    # filter fetch only results relative to the user
                                    followers.c.follower_id == self.id)
        # second query search for self user posts  
        own = Posts.query.filter_by(user_id = self.id)
        # all posts are combined and ordered with union statement
        return followed.union(own).order_by(Posts.timestamp.desc())

    def get_reset_password_token(self, exp_time = 900):
        """creates a token for authenticate of email link 

        :param exp_time: validity of the token in seconds, defaults to 900
        :type exp_time: int, optional
        :return: token
        :rtype: jwt token
        """	    
        token = jwt.encode(payload={'reset_password': self.id, 'exp': time() + exp_time}, key=current_app.config['SECRET_KEY'], algorithm='HS256')
        print('sent key:', current_app.config['SECRET_KEY'])
        return token
    
    @staticmethod # staticmethods can be invoked directly from the class. do not recive the class as firts argument
    def verify_reset_password_token(token):
        """verifies the authenticity of the token itself and returns the user with the ID stored in the token

        :param token: the token to verify
        :type token: jwt token
        :return: Users with the token ID
        :rtype: Users
        """
        try:   # if token is expired an exception is raised
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
            print(id)
        except:
            print('in the except')
            return
        return Users.query.get(id)

    # avatar pic--------------------
    def avatar(self, size:int)->str:
        """generate an avatar image form the md5 hash of the email and return a link to insert in the img tag in html

        :param size: the dimension in px of the image(128, 64, 32 etc)
        :type size: int
        :return: link to the source
        :rtype: str
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()  # obtain the digest of the md5 hash of the email
        return 'https://www.gravatar.com/avatar/{}?d=robohash&s={}&r=r'.format(digest, size)    # just the link of the service. can be added an r parameter fro the rating of the image (acc values are: g, pg, r, x)
    
    def __repr__(self):
        return'<User: {}>'.format(self.username)
    
class Posts(db.Model):
    id        = db.Column(db.Integer, primary_key = True)
    body      = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index = True, default=datetime.utcnow)  # utcnow is a function and is passed completely (without "()"), not the return value, so the timestamp is converted to the user's machine time
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id')) # how to set a foregin key. the user table is used, not the class User as above
    language  = db.Column(db.String(5))

    def __repr__(self):
        return '<Post: {}>'.format(self.body)
    

@login.user_loader
def load_user(id):
    return Users.query.get(int(id)) # querys the users id and convert into a int (only if is so saved in the databse's column)