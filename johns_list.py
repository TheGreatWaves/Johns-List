"""
Main application file.
Add and implement entry points here (We could move them out later if desired.)
"""

# Flask
from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, desc
import random
import logging

# For hashing
from werkzeug.security import generate_password_hash, check_password_hash

# Others
import yaml

# App, db and tables
from init_schema import *

# Load credentials
cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)

# Images for background of signup/signin
bg_images = ['https://thumbs.gfycat.com/BrightCleanAnkole-size_restricted.gif', 
             'https://geekymythology.files.wordpress.com/2018/10/howls-moving-castle-sophie-on-a-train.gif', 
             'https://i.gifer.com/3QvS.gif',
             'https://media2.giphy.com/media/XP3c8dMALpHxK/giphy.gif',
             'https://i.pinimg.com/originals/4e/99/f1/4e99f14687f913f793a66c15eaa52ae5.gif']


# Database credentials configurations 
app.config['SECRET_KEY'] = 'SECRET_KEY' # TODO: REMOVE THIS!

# Comment to disable logs
app.config['SQLALCHEMY_ECHO'] = True

#=========================================#
#       Short cute simple QoL utils       #
#=========================================#

# Check if user is logged in
def logged_in():
    return 'login' in session

# No need to perform query, just get username
def whoami_username():
    return session.get('username')

def whoami_id():
    return session.get('uid')

# Return current user
def whoami():
    if not logged_in():
        return None
    return User.query.filter_by(user_id=session['uid']).first()

def is_user(uid):
    if not logged_in():
        return False
    
    return whoami_id() == uid

def set_login(user):
    session['login'] = True
    session['username'] = user.username
    session['uid'] = user.user_id


# https://stackoverflow.com/questions/49245479/how-to-display-a-list-across-multiple-pages-in-flask
class SearchResult:
    
   def __init__(self, name, data, page, number):
     self.data = data
     self.page = int(page)
     self.number = int(number)
     self.full_listing = [self.data[i:i+number] for i in range(0, len(self.data), number)]
     self.name = name
     self.pages = len(self.full_listing)
     
   def __iter__(self):
     for i in self.full_listing[self.page - 1]:
       yield i
       
   def __repr__(self): #used for page linking
     return "/{name}/{page}".format(name=self.name, page=self.page + 1) #view the next page

#=========================================#
# INITILIAZE ENTRY POINTS BELOW THIS LINE #
#=========================================#

"""
/
/about/
/signup/
/signin/
/signout/
/user/<username>
/user/<username>/edit
/create_group/
/group/<group_name>/join
/group/<group_name>/leave
/group/<group_name>/edit
/group/<group_name>
/create_content/
/content/<content_type>/<content_title>
/content/search/
/content/<content_type>/<content_title>/edit
/content/<content_type>/<content_title>/me/add
/content/<content_type>/<content_title>/<group_id>/add
/<owner>/<owner_name>/<list_name>/
/content/<content_type>/<content_title>/modal/
"""

# Index
@app.route("/")
def index():
    contents = Content.query.filter(Content.poster != None).order_by(func.random()).limit(6)

    top_contents = Content.query.filter( Content.poster != None ).order_by( desc(Content.rating_score) ).limit(6)

    popular_contents = Content.query.filter( Content.poster != None ).order_by( desc(Content.number_of_ratings) ).limit(6)

    return render_template("index.html", contents=contents, top_contents=top_contents, popular_contents=popular_contents)

# About page
@app.route("/about/")
def about():
    return render_template("about.html")

# Sign up 
@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    img = random.choice(bg_images)
    if request.method == 'GET':
        return render_template('signup.html',img=img)

    elif request.method == 'POST':
        userDetails = request.form
        email = userDetails['email']
        username = userDetails['username']
        
        # Check that passwords matches
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Password does not match', 'danger')
            return render_template('signup.html',img=img, email=email, username=username)

        if email == "":
            flash('Email can not be blank', 'danger')
            return render_template('signup.html',img=img, username=username)

        if username == "":
            flash('Username can not be blank', 'danger')
            return render_template('signup.html',img=img, email=email)

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        # If user already exists...
        if existing_user:

            # Note: elif is used to prevent bombarding with flash

            # Email is in use
            if existing_user.email == email:
                flash('Email already in use', 'danger')
                return render_template('signup.html',img=img, username=username)
            # Usernname is in use
            elif existing_user.username == username:
                flash('Username unavailable', 'danger')
                return render_template('signup.html',img=img, email=email)
            
            return render_template('signup.html',img=img)
    
        pw = userDetails['password']
        hashed_pw = generate_password_hash(pw)
        new_user = User(email=email, username=username, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Successfully registered', 'success')

        # Redirect user to sign in page upon success
        return redirect('/signin/')    

    return render_template('signup.html',img=img)

# Sign in
@app.route("/signin/", methods=['GET', 'POST'])
def signin():
    img = random.choice(bg_images)
    if request.method == 'GET':
        
        # Safe guard
        if logged_in():
            return redirect('/')

        return render_template('signin.html', img=img)

    elif request.method == 'POST':
        
        loginForm = request.form
        user_input = loginForm['email_or_user']
        
        # Query for user entry
        found = User.query.filter((User.email == user_input) | (User.username == user_input)).first()
        
        # Try finding
        if found is not None:
            
            # Found, check password
            if check_password_hash(found.password, loginForm['password']):

                # Log session info
                session['login'] = True
                session['username'] = found.username
                session['uid'] = found.user_id
                flash('Welcome ' + session['username'],'success')

                # If we were redirected to login, we want to 
                # redirect back to where-ever we were sent from
                if 'last_page' in session:
                    return redirect(session['last_page'])

                # Otherwise just go to home page
                return redirect('/')
            else:
                # Wrong password
                flash("Incorrect credentials", 'danger')
                return render_template('signin.html', img=img)

        else:
            # No existing user with given email/username
            flash('User not found', 'danger')
            return render_template('signin.html', img=img)
    
    return render_template('signin.html',img=img)

# Sign out
@app.route('/signout/')
def signout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

# User profile page
@app.route('/user/<username>', methods=['GET'])
def user(username):

    # Find user using username
    user = User.query.filter_by(username=username).first()

    # User not found
    if user is None:
        flash("User not found", 'danger')
        
        if username == whoami_username():
            session.clear()
        
        return redirect('/')

    # Get all groups the user is in
    user_groups = user.get_all_groups()\
                    .order_by(Group.name)\
                    .all()

    is_owner = whoami_username() == user.username

    return render_template('user.html', user=user, groups=user_groups, is_owner=is_owner)

# Edit user profile page
@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def edit_user(username):

    # Find user using username
    user = User.query.filter_by(username=username).first()

    if request.method == 'GET':

        # User not found
        if user is None:
            flash("User not found", 'danger')
            
            if username == whoami_username():
                session.clear()
            
            return redirect('/')

        is_owner = whoami_username() == user.username

        # Get Groups owned by the user
        groups_owned = Group.query.filter_by(owner_id=user.user_id)
        
        user.get_all_groups()\
                        .filter_by()\
                        .order_by(Group.name)\
                        .all()
        
        if not is_owner:
            flash("You don't have permisssion to edit", 'danger')
            return redirect(url_for( 'user', username=username))
        else:
            return render_template('edit_user.html', user=user, owned_groups=groups_owned)
        
    elif request.method == 'POST':

        form = request.form
        
        new_username = form['username']
        new_user_pfp = form['user_pfp']
        new_user_bio = form['user_bio'] # + "\n" + user.password + "\n" + generate_password_hash('123')
        old_password = form['old_password']
        new_password = form['new_password']
        confirm_password = form['confirm_password']

        print('NEW USERNAME: ', new_username)
            
        if new_user_pfp == "":
            new_user_pfp = url_for('static', filename='place_holder_img.png')
        
        # existing username
        existing_name = User.query.filter(User.username == username).first()

        error = False

        if new_username  == "":
            flash( 'Username cannot be empty', 'danger' )
            error = True
        elif existing_name and existing_name.username != username:
            flash('This name has already been taken', 'danger')
            error = True
        
        if (old_password or new_password or confirm_password):
            if not (old_password and new_password and confirm_password):
                flash('Missing password', 'danger')
                error = True

            if old_password and not check_password_hash(user.password, old_password):
                flash('Old password is incorrect', 'danger')
                error = True

            if new_password != "" and confirm_password != "" and new_password != confirm_password:
                flash('Password does not match', 'danger')
                error = True
        
        if error:
            return redirect(url_for( 'edit_user', username=username))
        
        # Update user info
        user.username = new_username


        if is_user(user.user_id):
            set_login(user)

        user.profile_pic_url = new_user_pfp
        user.bio = new_user_bio
        if new_password:
            user.password = generate_password_hash(new_password)
        db.session.commit()
            
        # Success message
        flash('User Info edited successfully', 'success')
        return redirect( url_for('user', username=user.username) )

    return redirect( url_for('user', username=username) )

@app.route('/create_group/', methods=['GET', 'POST'])
def create_group():
    
    if request.method == 'GET':

        # Redirect to login if not
        if not logged_in():
            session['last_page'] = url_for('create_group')
            return redirect(url_for('signin'))
        
        return render_template('create_group.html')

    elif request.method == 'POST':

        group_name = request.form['group_name']
        
        # Check if group name is valid
        if group_name == "":
            flash('Group name can not be empty', 'danger')
            return redirect(url_for('create_group'))

        found = Group.query.filter_by(name=group_name).first()
       
        # If found, group name has been taken
        if found:
            flash('Group name already taken', 'danger')
            return redirect(url_for('create_group'))

        # Create the new group
        new_group = Group(name=group_name, owner=whoami())
        
        # Can't set inside init_schema
        new_group.img_url = url_for('static', filename='place_holder_img.png')
    
        # Save changes
        db.session.add(new_group)
        db.session.commit()

        flash(f'New group [{group_name}] successfully created!', 'success')
        
        # Redirect to the new group's page
        return redirect(url_for('group', group_name=group_name))
    else:
        return render_template('create_group.html')

# Join Group
# NOTE: This url should be only available
#       when the user IS logged in.
@app.route('/group/<group_name>/join')
def join_group(group_name):
    
    if not logged_in():
        session['last_page'] = url_for('join_group', group_name=group_name)
        return redirect(url_for('signin'))

    # Get target group and current user
    group = Group.query.filter_by(name=group_name).first()
    user = whoami()
    
    # Check if we're in group
    in_group = group.has_member(user.user_id)

    if in_group:
        flash('Already in group!', 'danger')
        return redirect(url_for('group', group_name=group_name))

    group.add_member(user)
    db.session.commit()

    flash('Joined group!', 'success')

    return redirect(url_for('group', group_name=group_name))

# Leave Group
@app.route('/group/<group_name>/leave')
def leave_group(group_name):
    
    group_q = Group.query.filter_by(name=group_name)
    group = group_q.first()
    user = whoami()

    # Check if we're in the group
    in_group = group.has_member(user.user_id)

    # User is in group, remove them.
    if in_group:
        group.remove_member(user)
        db.session.commit()
        
        # Group has no members, disband.
        if group.empty():
            
            # Clear list ( so all foreign keys are let-go )
            group.lists = []
            
            # Delete the group
            group_q.delete()
            
            db.session.commit()
            flash('Group disbanded!', 'success')
            return redirect('/')

        flash('Successfully left group!', 'success')

        return redirect(url_for('group', group_name=group.name))
    
    # We're trying to leave, but we
    # are not in the group
    flash('Not in group!', 'danger')
    return redirect(url_for('group', group_name=group.name))

@app.route('/group/<group_name>/edit', methods=['GET', 'POST'])
def edit_group(group_name):
    group = Group.query.filter_by(name=group_name).first()
    if group is None:
        flash("Group not found", 'danger')
        return redirect('/')
    
    # Get list of all members
    members_q = group.get_all_members()
    members = group.get_all_members().all()

    who = whoami_id()
    is_owner = who == group.owner_id
    is_member = members_q.filter(User.user_id == who).first()
    if request.method == 'GET':
        if not logged_in():
            session['last_page'] = url_for('edit_group', group_name=group.name)
            return redirect(url_for('signin'))
            
        return render_template('edit_group.html', group=group, members=members, is_member=is_member, is_owner=is_owner)
    elif request.method == 'POST':
        form = request.form
        group_name = form['group_name'] if is_owner else group.name
        group_img = form['group_img']
        group_info = form['group_info']

        if group_name  == "":
            flash( 'Group name cannot be empty', 'danger' )
            return redirect( url_for( 'edit_group', group_name=group.name ) )
            
        if group_img == "":
            group_img = url_for('static', filename='place_holder_img.png')
                
        # existing group name
        existing_name = Group.query.filter(Group.name == group_name).first()
        if existing_name and existing_name.name != group.name:
            flash('This name has already been taken', 'danger')
            return redirect(url_for('edit_group', group_name=group.name ))
                
        # Update group    
   
        group.name = group_name
        group.info = group_info
        group.img_url = group_img
        db.session.commit()
            
        # Success message
        flash('Group edited successfully', 'success')

    return redirect(url_for('group', group_name=group.name))


# Group
@app.route('/group/<group_name>', methods=['GET'])
def group(group_name):

    # Find user using username
    group = Group.query.filter_by(name = group_name).first()

    if group is None:
        flash("Group not found", 'danger')
        return redirect('/')

    # Get list of all members
    members_q = group.get_all_members()
    members = members_q.all()
    
    if not logged_in():
        return render_template('group.html', group=group, members=members, is_member=None, unknown_user=True)


    # Find out if current user is in the member list
    # Note: I didn't use Group.has_member(uid) because this
    #       query should be much cheaper to compute.
    is_member = members_q.filter(User.user_id == whoami().user_id).first()

    return render_template('group.html', group=group, members=members, is_member=is_member)
    
# Content related...

# Create content page
@app.route('/create_content/', methods=['GET', 'POST'])
def create_content():
    if request.method == 'GET':
        
        if not logged_in():
            session['last_page'] = url_for('create_content')
            return redirect(url_for('signin'))
        
        return render_template('create_content.html')
    
    elif request.method == 'POST':
        form = request.form
        content_title = form['content_title']
        content_type = form['content_type']
        
        # blank input
        if content_title == "":
            flash('Content title can not be empty', 'danger')
            return redirect('/create_content/')
            
        # existing content
        found = Content.find_by_name_and_type(content_title, content_type)
        
        if found:
            flash('Content already exist', 'danger')
            return redirect('/create_content/')
            
        # Make new content
        new_content = Content(content_title, content_type)
        new_content.poster = url_for('static', filename='place_holder_img.png')
        
        db.session.add(new_content)
        db.session.commit()
        
        # Success message
        flash('Content added successfully', 'success')
   
        return redirect(url_for('content', content_id=new_content.content_id, content_type=content_type))
    
    return render_template('create_content.html')
    
@app.route('/content/<content_type>/<content_id>', methods=['GET','POST'])
def content(content_type, content_id):
    if request.method == 'GET':
        found = Content.search(content_id)
        
        if found:
            rating = found.get_total_rating()
            has_content = 0
            
            if logged_in():

                list = whoami().lists
                
                if list[List.WATCH_LIST].has_content(found):
                    has_content = 1
                
                if list[List.COMPLETED_LIST].has_content(found):
                    has_content = 2
        
            return render_template('content.html', content=found, rating=rating, has_content=has_content)
        else:
            flash('Content page not found', 'danger')
            return redirect('/')
    
    elif request.method == 'POST':
        return redirect(url_for('edit_content',content_type=content_type, content_id=content_id))

# Search for content by title
    
@app.route('/content/search/', methods=['GET', 'POST'])
def search_content():
    if request.method == 'GET':
        return render_template('search_content.html', contents=None)
    elif request.method == 'POST':
        content_title = request.form['content_title']
        
        if content_title == "":
            content_title = "all"
        
        return redirect(url_for('search_content_results', search_name=content_title, pagenum=1))
    return render_template('search_content.html')

@app.route('/content/search/<search_name>/result/<pagenum>', methods=['GET', 'POST'])
def search_content_results(search_name, pagenum):
    
    if request.method == 'GET':
        if search_name == "all":
            search_name = "%%"
        else:
            search_name = "%{}%".format(search_name)

        contents = Content.query.filter(Content.title.like(search_name)).order_by(Content.title).all()
        
        # Set up the pagination
        number_of_results = 10
        results = SearchResult(f'/content/search/{search_name}/result/{pagenum}', contents, pagenum, number_of_results)
        results.next = url_for('search_content_results', search_name=search_name, pagenum=int(pagenum)+1)
        results.prev = url_for('search_content_results', search_name=search_name, pagenum=int(pagenum)-1)
   
        return render_template('search_content.html', contents=results)
    elif request.method == 'POST':
        content_title = request.form['content_title']
        if content_title == "":
            content_title = "all"
        return redirect(url_for('search_content_results', search_name=content_title, pagenum=1))


@app.route('/content/<content_type>/<content_id>/edit', methods=['GET', 'POST'])
def edit_content(content_type, content_id):
    if request.method == 'GET':
        found = Content.search(content_id)
        tags = None
        if found:
            content_type = found.content_type
            tags = ''.join([str(tag.name) + ', ' for tag in found.genres])[0: -2]

        if not logged_in():
            session['last_page'] = url_for('edit_content',content_type=content_type, content_id=content_id)
            return redirect(url_for('signin'))
        
        return render_template('edit_content.html', content=found, tags=tags)

    elif request.method == 'POST':
        content = Content.search(content_id)
        
        cid                 = content.content_id
        form                = request.form
        content_title       = form['content_title']
        content_img         = form['content_img']
        content_synopsis    = form['content_synopsis']
        content_status      = form['content_status']
        content_tags        = form['tags']
        adpt                = form.get('adaptation')
        season              = form['season']
        sequel              = form.get('sequel')
        prequel             = form.get('prequel')
        
        # Basic setup for sequel/prequel
        if (sequel.lower() == "none" or sequel == ""):
            content.remove_sequel()
        
        if (prequel.lower() == "none" or prequel == ""):
            content.remove_prequel()
            
        # Sequel setup
        alreadyHasSequel = len(content.sequel) > 0
        
        # Prequel setup
        found = content.prequel
        alreadyHasPrequel = found != None
            
        
        # Assign Sequel
        if sequel and sequel.lower() != "none":
            
            newNotSameAsOld = not alreadyHasSequel or not content.has_sequel(sequel)
            
            if newNotSameAsOld:
                
                search_content = Content.search(sequel)
                
                if search_content is None:
                    flash( 'No sequel content found', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
               
                # Avoid circular dependency
                if content.title == search_content.title:
                    flash( 'Invalid sequel entry, self referential error', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
               
                # Clashes with prequel
                if alreadyHasPrequel and search_content.title == content.prequel.title:
                    flash( 'Sequel and prequel can not be the same', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
                
                content.set_sequel( search_content )
        # Got blank or none
        else: 
            if content.sequel:
                content.sequel = [] # Delete the sequel
        
         # Assign Prequel
        if prequel and prequel.lower() != "none":
        
            newNotSameAsOld = not alreadyHasPrequel or prequel != found.sequel[0].title
            
            if newNotSameAsOld:
                search_content = Content.search(prequel)
                
                if search_content is None:
                    flash( 'No prequel content found', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
                    
                # Avoid circular dependency
                if content.title == search_content.title:
                    flash( 'Invalid prequel entry, self referential error', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
                
                # Clashes with sequel
                if alreadyHasSequel and content.has_sequel(prequel):
                    flash( 'Sequel and prequel can not be the same', 'danger' )
                    return redirect( url_for( 'edit_content',content_type=content_type, content_id=content_id ) )
                
                content.set_prequel( search_content )
        # Got blank or none
        else: 
            content.remove_prequel()
        
        if season != "":
            content.season = season
            
            if season.lower() == "none":
                content.season = None
        
        if adpt:
            if adpt != "" and adpt.lower() != "none":
                
                found = None
                
                if adpt.isnumeric():
                    found = Content.find_by_id(adpt)
                else:
                    found = Content.query\
                        .filter(Content.title.like("%{}%".format(adpt)))\
                        .filter((Content.content_id != content.content_id) & (Content.content_type != content.content_type))\
                        .first()
                
                if found:
                    content.set_adaptation(found)
                else:
                    content.disconnect_source()
                    flash('Adaptation not found', 'danger')
            elif adpt.lower() == "none":
                content.disconnect_source()
        
        if content_tags != "":
            tags = content_tags.split(", ")
            
            # Add all tags (will skip dupes automatically)
            for tag in tags:
                content.set_genre(Genre(tag))
            
            # Remove tags we don't have anymore
            for tag in content.genres:
                if tag.name not in tags:
                    content.genres.remove(tag)

        # blank input
        if content_title == "":
            flash('Content title can not be empty', 'danger')
            return redirect(url_for('edit_content',content_type=content_type, content_id=content_id))
        
        if content_img == "":
            content_img = '/static/place_holder_img.png'

        if content_synopsis == "":
                content_synopsis = 'No sypnosis has been provided.'
                
        if content_status == "":
            content_status = -1
            
        # existing content
        found = Content.find_by_name_and_type(content_title, content_type)
        if found:
            if found.title != content_title:
                flash('This content has its own page already', 'danger')
                return redirect(url_for('edit_content',content_type=content_type, content_id=content_id))
            
        # Update content    
        content.title = content_title
        content.synopsis = content_synopsis
        content.poster = content_img
        content.status = content_status
        db.session.commit()
        
        # Success message
        flash('Content edited successfully', 'success')
   
        return redirect(url_for('content', content_id=cid, content_type=content_type))


@app.route('/content/<content_type>/<content_id>/me/add', methods=['GET'])
def list_add_content(content_type, content_id):
    
    # Handle login
    if not logged_in():
        session['last_page'] = url_for('list_add_content', content_type=content_type, content_id=content_id)
        return redirect(url_for('signin'))
    
    user = whoami()
    content = Content.search( content_id )
    
    if content:
        if not user.lists[List.WATCH_LIST].has_content(content):
            flash(f'Added to watch list', 'success')
            user.lists[List.WATCH_LIST].add(content)
            db.session.commit()
        else:
            flash(f'Content already in list', 'danger')
            
    else:
        flash(f'Action failed', 'danger')
        
    return redirect(url_for('content', content_id=content_id, content_type=content_type))

@app.route('/content/<content_type>/<content_id>/me/remove/', methods=['GET'])
def list_remove_content(content_type, content_id):
    
    # Handle login
    if not logged_in():
        session['last_page'] = url_for('list_add_content', content_type=content_type, content_id=content_id)
        return redirect(url_for('signin'))
    
    user = whoami()
    content = Content.search(content_id)
    
    if content:
        if user.lists[List.COMPLETED_LIST].has_content(content):
            flash(f'Removed from completed list', 'success')
            user.lists[List.COMPLETED_LIST].remove(content)
            db.session.commit()
        elif user.lists[List.WATCH_LIST].has_content(content):
            flash(f'Removed from watch list', 'success')
            user.lists[List.WATCH_LIST].remove(content)
            db.session.commit()
        else:
            flash(f'Content already not in list', 'danger')
            
    else:
        flash(f'Action failed', 'danger')
        
    return redirect(url_for('content', content_id=content.id, content_type=content_type))

@app.route('/content/<content_type>/<content_id>/<group_id>/add', methods=['GET'])
def group_list_add_content(content_type, content_id, group_id):
    
    # Handle login
    if not logged_in():
        session['last_page'] = url_for('group_list_add_content', content_type=content_type, content_id=content_id, group_id=group_id)
        return redirect(url_for('signin'))
    
    group = Group.query.filter_by(group_id = group_id).first()
    content = Content.search(content_id)
    
    if content:
        if not group.lists[List.WATCH_LIST].has_content(content):
            flash(f'Content successfully added to {group.name}\'s watch list', 'success')
            group.lists[List.WATCH_LIST].add(content)
            db.session.commit()
        else:
            flash(f'Content already in list', 'danger')
            
    else:
        flash(f'Action failed', 'danger')
        
    return redirect(url_for('content', content_id=content_id, content_type=content_type))
    
@app.route('/<owner>/<owner_name>/<list_name>/', methods=['GET', 'POST'])
def list(owner, owner_name, list_name):
    if request.method == 'GET':
        
        list = None
        name = None
        
        # Owner can either be a group or user
        list_owner = User.query.filter_by(username=owner_name).first() \
            or Group.query.filter(Group.name==owner_name).first()
        
        # No owner found
        if list_owner is None:
            flash('User not found', 'danger')
            return redirect('/')
        
        # Get the list
        if list_name=="watchlist":
            list = list_owner.lists[List.WATCH_LIST]
        elif list_name=="completed":
            list = list_owner.lists[List.COMPLETED_LIST]
        else:
            flash('Error finding list', 'danger')
            return redirect('/')
        
        name = list_owner.username if hasattr(list_owner, "username") else list_owner.name
        user = whoami()
        
        # For list editting permissions (either owner or member of group)
        
        is_owner = False
        
        if list.owner_class == 'u':
            is_owner = is_user(owner_name)
        elif list.owner_class == 'g':
            is_owner = ((list_owner.has_member(whoami_id()) != None) if user is not None else False) 
    
        return render_template('list.html', owner_name=name, list=list, is_owner=is_owner)
    
    elif request.method == 'POST':
        
         # Owner can either be a group or user
        list_owner = User.query.filter_by(username=owner_name).first() \
            or Group.query.filter(Group.name==owner_name).first()
            
        watchlist = list_name=="watchlist"
        
        # Get content id from button
        content_id = request.form.get('complete') or request.form.get('remove')
        content = Content.query.filter_by(content_id=content_id).first()
        
        if watchlist:
            if 'complete' in request.form:
                list_owner.lists[List.WATCH_LIST].remove(content)
                list_owner.lists[List.COMPLETED_LIST].add(content)
                db.session.commit()
            elif 'remove' in request.form:
                list_owner.lists[List.WATCH_LIST].remove(content)
                db.session.commit()
        else:
            if 'remove' in request.form:
                list_owner.lists[List.COMPLETED_LIST].remove(content)
                db.session.commit()
        
        return redirect(url_for('list', owner=owner, owner_name=owner_name, list_name=list_name))
    return redirect(url_for('list', owner=owner, owner_name=owner_name, list_name=list_name))
    
@app.route("/content/<content_type>/<content_id>/modal/", methods=['GET', 'POST'])
def list_add_modal(content_type, content_id):
    if request.method == 'GET':
        
        
        # Handle login
        if not logged_in():
            session['last_page'] = url_for('list_add_modal', content_type=content_type, content_id=content_id)
            return redirect(url_for('signin'))
        
        found = Content.search(content_id)
        
        if found:
            
            user_groups = whoami().get_all_groups()\
                    .order_by(Group.name)\
                    .all()
            
            rating = found.get_total_rating()
            
            return render_template('list_add_modal.html', content=found, groups=user_groups, rating=rating)
        else:
            flash('Content page not found', 'danger')
            return redirect('/')
    
    elif request.method == 'POST':
        return redirect(url_for('edit_content',content_type=content_type, content_id=content_id))

@app.route('/content/<content_type>/<content_id>/rate', methods=['GET','POST'])
def rate_content(content_type, content_id):
    if request.method == 'GET':
        # Handle login
        if not logged_in():
            session['last_page'] = url_for('content', content_type=content_type, content_id=content_id)
            return redirect(url_for('signin'))
        
        content = Content.search( content_id )
        if content:
            rating = content.get_total_rating()
            return render_template('set_rating_modal.html',content=content, rating=rating)
        else:
            return render_template('content', content_type=content_type, content_id=content_id)
        
    elif request.method == 'POST':  
        
        if not logged_in():
            session['last_page'] = url_for('content', content_type=content_type, content_id=content_id)
            return redirect(url_for('signin'))

        user = whoami()
        content = Content.search( content_id )
        rating = request.form["slider"]
        
        if content:
            action = content.set_rating(user.user_id, rating)
            
            if action == Rating.ADDED_RATING:
                flash('Rating added', 'success')
            elif action == Rating.EDITTED_RATING:
                flash('Rating editted', 'success')
            
            db.session.commit()
            return redirect( url_for('content', content_type=content_type, content_id=content_id))
                
        flash('no content found', 'danger')
        return redirect('/')

@app.route("/content/<content_type>/<content_id>/rate_modal/", methods=['GET', 'POST'])
def set_rating_modal(content_type, content_id):
    if request.method == 'GET':
        return redirect(url_for('rate_content',content_type=content_type, content_id=content_id))
    
    if request.method == 'POST':
        return redirect(url_for('rate_content',content_type=content_type, content_id=content_id))

# Search Group/Users
@app.route('/search/', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        
        search_input = request.form['user_input']
        search_param = request.form['search_param']
        
        search_name = "%{}%".format(search_input)
        found = None
 
        match search_param:
            case "group":
                found = Group.query.filter(Group.name.like(search_name)).order_by(Group.name).all()
            case "user":
                found = User.query.filter(User.username.like(search_name)).order_by(User.username).all()
        
        return render_template('search.html', results=found, category=search_param)

@app.route('/tag/<tag>/<pagenum>')
def search_tag(tag, pagenum):
    tag = Genre.query.filter_by(name = tag).first()
    
    # Set up the pagination
    number_of_results = 10
    results = SearchResult(f'tag/{tag}', tag.contents, pagenum, number_of_results)
    results.next = url_for('search_tag', tag=tag, pagenum=int(pagenum)+1)
    results.prev = url_for('search_tag', tag=tag, pagenum=int(pagenum)-1) 

    return render_template('search_content.html', tag=tag.name, contents=results)

#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#

# Main program entry point
if __name__ == '__main__':  
    app.run(debug=True)



