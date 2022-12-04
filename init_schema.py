"""
This is ONLY responsible for creating tables.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask import Flask, url_for

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

# Membership (many-to-many)
group_member_table = db.Table('group_member',
    db.Column('member_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.group_id'))
)

# User table
class User( db.Model ):
    user_id = db.Column('user_id', db.Integer, primary_key = True, autoincrement=True)
    user_class = db.Column('user_class', db.CHAR(1), primary_key = True, default='u')
    name = db.Column(db.String(20), default='None')
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255))
    registered_date = db.Column(db.Date, default=date.today())
    profile_pic = db.Column(db.LargeBinary)
    
    lists = db.relationship('List', lazy='select',
        backref=db.backref('user', lazy='joined'))
    
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

    def get_all_groups(self):
        return Group.query.join(group_member_table)\
            .join(User)\
            .filter((group_member_table.c.member_id == User.user_id) & (group_member_table.c.group_id == Group.group_id))\
            .filter(User.user_id == self.user_id)




# Group table
class Group( db.Model ):
    group_id = db.Column('group_id', db.Integer, primary_key = True, autoincrement = True)
    group_class = db.Column('group_class', db.CHAR(1), primary_key = True, default='g')
    name = db.Column(db.String(20), unique=True, nullable=False)
    size = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  

    members = db.relationship('User',
        secondary = group_member_table,
        lazy='subquery',
        backref=db.backref('groups', lazy=True))
    
    lists = db.relationship('List', lazy='select',
        backref=db.backref('group', lazy='joined'))

    def get_member_count(self):
        return Group.query.join(Group.members).filter(Group.group_id == self.group_id).count()


    def get_all_members(self):
        return User.query.join(group_member_table)\
            .join(Group)\
            .filter((group_member_table.c.member_id == User.user_id) & (group_member_table.c.group_id == Group.group_id))\
            .filter(Group.group_id == self.group_id)

    def has_member(self, uid):
        member = Group.query.join(group_member_table).join(User)\
            .filter((group_member_table.c.member_id == uid) & (group_member_table.c.group_id == self.group_id))\
            .first() 
            
        return member is not None

    def __init__(self, name):
        self.name = name

class Content( db.Model ):
    content_id = db.Column( 'content_id', db.Integer, primary_key = True, autoincrement = True )
    title = db.Column( db.String(100), nullable=False )
    status = db.Column( db.Integer )
    genre = db.Column( db.String(20) )
    theme = db.Column( db.String(40) )
    demographic = db.Column( db.String(7) )
    content_type = db.Column( db.CHAR(5) )
    season = db.Column( db.Integer )
    duration = db.Column( db.Integer )
    poster = db.Column( db.String(300) )
    synopsis = db.Column( db.String(2000) )
    
    def __init__(self, title, content_type):
        self.title = title
        self.content_type = content_type
        self.poster = url_for('static', filename='place_holder_img.png')
        self.synopsis = "No synopsis has been provided."
        
    def find(name, type):
        return Content.query.filter((Content.title == name) & (Content.content_type == type)).first()


# M-2-M relationship between list and content
list_contents_table = db.Table('list_contents_table',
    db.Column('list_id', db.Integer, db.ForeignKey('list.list_id')),
    db.Column('content_id', db.Integer, db.ForeignKey('content.content_id'))
)

class List( db.Model ):
    list_id = db.Column( db.Integer, primary_key = True, autoincrement = True)
    
    # For users
    user_id = db.Column( db.Integer, db.ForeignKey("user.user_id"), nullable=True )
    
    # For groups
    group_id = db.Column( db.Integer, db.ForeignKey("group.group_id"), nullable=True )

    
    @hybrid_property
    def owner_id(self):
        return self.user_id or self.group_id
    
    owner_class = db.Column( db.CHAR(1), nullable=False )
    
    name = db.Column( db.String(30) )
    type = db.Column( db.CHAR(5) )
    desc = db.Column( db.String(1000) )
    
    contents = db.relationship('Content',
        secondary = list_contents_table,
        lazy='subquery',
        backref=db.backref('contents', lazy=True))
    
    WATCH_LIST = 0
    COMPLETED_LIST = 1
    
    def has_content(self, content):
        
        return List.query.join(list_contents_table)\
            .join(Content)\
            .filter((list_contents_table.c.list_id == self.list_id) & (list_contents_table.c.content_id == content.content_id)).count() > 0\
    
    def add(self, content):
        if not self.has_content(content):
            self.contents.append(content)
            
    def remove(self, content):
        if self.has_content(content):
            self.contents.remove(content)
    
    def __init__(self, owner_id, owner_class):
        
        self.owner_class = owner_class
        
        if owner_class=='u':
            self.user_id = owner_id
        elif owner_class=='g':
            self.group_id = owner_id
        else:
            self.user_id = 'u'
            
        
    
#=============================#
# END OF TABLE INITIALIZATION #
#=============================#

# Initialize all tables (Note this will also drop all previously existing tables)
if __name__ == '__main__':  
    with app.app_context():
        db.drop_all()
        db.create_all()



