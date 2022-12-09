"""
This is ONLY responsible for creating tables.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask import Flask, url_for
import random # For random pfp
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

# For fun
default_pfp = \
    [
        "https://i.pinimg.com/736x/6e/f4/ca/6ef4caa2da03b1fb9e4a00563c76ef5a.jpg",
        "https://i.pinimg.com/originals/2c/73/6a/2c736aa4d61d22e3946e73cbc37d9e06.jpg",
        "https://i.pinimg.com/originals/09/fa/83/09fa83a152b6100c00896b667be2606f.jpg",
        "https://i.pinimg.com/originals/78/6b/44/786b44076c4a7bb58da5aea354e7033b.jpg",
        "https://i.pinimg.com/originals/9b/2f/ac/9b2face9ba26d8db7567dd157913f63f.jpg",
        "https://i.pinimg.com/736x/d1/34/07/d1340745c4aaa9ee1c6952e793765bb7.jpg",
    ]


# User table
class User( db.Model ):
    user_id         = db.Column('user_id', db.Integer, primary_key = True, autoincrement=True)
    user_class      = db.Column('user_class', db.CHAR(1), primary_key = True, default='u')
    name            = db.Column(db.String(20), default='None')
    email           = db.Column(db.String(255), unique=True, nullable=False)
    username        = db.Column(db.String(20), unique=True, nullable=False)
    password        = db.Column(db.String(255))
    registered_date = db.Column(db.Date, default=date.today())
    bio             = db.Column(db.String(1000), default='There is nothing noteworthy about me.')
    profile_pic_url = db.Column( db.String(300) )
    
    lists = db.relationship('List', lazy='select',
        backref=db.backref('user', lazy='joined'))
    
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
        
        # Can't use url_for here without context, so
        # we have to manuallly set it here.
        self.profile_pic_url = random.choice(default_pfp)
        
        # Create the watchlist and completed list for user
        watch_list = List(self.user_id, 'u', 'watchlist')
        completed_list = List(self.user_id, 'u', 'completed')
        
        self.lists.append(watch_list)       # At index 0
        self.lists.append(completed_list)   # At index 1
        
    def get_all_groups(self):
        return Group.query.join(group_member_table)\
            .join(User)\
            .filter((group_member_table.c.member_id == User.user_id) & (group_member_table.c.group_id == Group.group_id))\
            .filter(User.user_id == self.user_id)




# Group table
class Group( db.Model ):
    group_id    = db.Column('group_id', db.Integer, primary_key = True, autoincrement = True)
    group_class = db.Column('group_class', db.CHAR(1), primary_key = True, default='g')
    name        = db.Column(db.String(20), unique=True, nullable=False)
    owner_id    = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    info        = db.Column( db.String(2000) )
    size        = db.Column(db.Integer, default=0)
    img_url     = db.Column( db.String(300) )

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
    
    def set_default_info(self):
        self.info = f"Nothing provided"

    def __init__(self, name, owner: User):
        self.name = name
        self.owner_id = owner.user_id
        self.size = 0
        self.add_member(owner)
        
        # Add lists
        group_watch_list = List(self.group_id, 'g', 'watchlist')
        group_completed_list = List(self.group_id, 'g', 'completed')
        self.img_url = "https://geodash.gov.bd/uploaded/people_group/default_group.png"
        self.set_default_info()
        
        self.lists.append(group_watch_list)        # At index 0
        self.lists.append(group_completed_list)    # At index 1
        
    def add_member(self, user):
        self.members.append(user)
        self.size += 1
    
    def remove_member(self, user):
        self.members.remove(user)
        self.size -= 1
        
    def empty(self):
        return self.size <= 0
        


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
        self.poster = None
        self.synopsis = "No synopsis has been provided."
        
    def find(name, type):
        return Content.query.filter((Content.title == name) & (Content.content_type == type)).first()

    ratings = db.relationship('Rating', backref='content')

    def get_all_rating_q(self):
        return self.query.join(Rating)

    def get_rating_count(self):
        return self.get_all_rating_q().count()

    def get_all_rating(self):
        return self.get_all_rating_q().all()

    def get_rating(self,uid):
        return Rating.query.filter_by(user_id=uid, content_id=self.content_id).first()

    def add(self, uid, score):
        rating = Rating(uid, score)
        self.ratings.append(rating)
        return rating

    def set_rating( self, uid, score ):
        
        rating = self.get_rating(uid)
        
        if rating is None:
            self.add(uid, score)
            return Rating.ADDED_RATING
        else:
            rating.content_rating = score
            return Rating.EDITTED_RATING


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
    type = db.Column( db.CHAR(5))
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
    
    def __init__(self, owner_id, owner_class, name):
        
        self.owner_class = owner_class
        self.name = name
        
        if owner_class=='u':
            self.user_id = owner_id
        elif owner_class=='g':
            self.group_id = owner_id
        else:
            self.user_id = 'u'
            


class Rating( db.Model ):
    rat_id = db.Column( db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column( db.Integer, db.ForeignKey("user.user_id"), nullable=True )
    content_id = db.Column( db.Integer, db.ForeignKey("content.content_id"), nullable=False )
    content_rating = db.Column( db.Integer())

    # Some constants
    ADDED_RATING   = 0
    EDITTED_RATING = 1

    def __init__(self, uid, rating):
        self.user_id = uid
        self.content_rating = rating
    
class Person( db.Model ):
    pid = db.Column( db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column( db.String(20) )
    last_name = db.Column( db.String(20) )
    DOB = db.Column(db.Date, nullable=True, default=None)
        
        
class Company( db.Model ):
    com_id = db.Column( db.Integer, primary_key=True, autoincrement=True)
    com_name = db.Column( db.String(20) )
    com_est = db.Column(db.Date, nullable=True, default=None)
    
class Status( db.Model ):
    id = db.Column( db.Integer, primary_key=True, autoincrement=False)
    status = db.Column( db.String(11) )
    
class Format( db.Model ):
    content_type = db.Column( db.String(5), primary_key=True )
    format_type = db.Column( db.String(15) )

class Genre( db.Model ):
    genre_type = db.Column( db.String(20), primary_key=True, nullable=False)
    explicit = db.Column( db.Boolean, default=False, nullable=True )
    
class Job( db.Model ):
    id = db.Column( db.Integer, primary_key=True)
    name = db.Column( db.String(20) )
    
    
#=============================#›
# END OF TABLE INITIALIZATION #
#=============================#

def create():
    db.drop_all()
    db.create_all()

# Initialize all tables (Note this will also drop all previously existing tables)
if __name__ == '__main__':  
    with app.app_context():
        create()



