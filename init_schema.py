"""
This is ONLY responsible for creating tables.
"""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

import yaml

# Load credentials
cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)

# For Date
from datetime import date

# Intialize flask app
app = Flask(__name__)

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + cred['mysql_user'] + ':' + cred['mysql_password'] + '@' + cred['mysql_host'] + '/' + cred['mysql_db']
app.config['SQLALCHEMY_ECHO'] = True # Comment to disable logs

# Connect app's db to SQLAlchemy
db = SQLAlchemy(app)

#===================================#
# INITILIAZE TABLES BELOW THIS LINE #
#===================================#

# User table
class User(db.Model):
   user_id = db.Column('user_id', db.Integer, primary_key = True, autoincrement=True)
   user_class = db.Column('user_class', db.CHAR(1), primary_key = True, default='u')
   name = db.Column(db.String(20), default='None')
   email = db.Column(db.String(255))
   username = db.Column(db.String(20))
   password = db.Column(db.String(255))
   registered_date = db.Column(db.Date, default=date.today())
   profile_pic = db.Column(db.LargeBinary)
  

def __init__(self, email, username, password):
    self.email = email
    self.username = username
    self.password = password

#=============================#
# END OF TABLE INITIALIZATION #
#=============================#

# Initialize all tables
if __name__ == '__main__':  
    with app.app_context():
        db.create_all()



