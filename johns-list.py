"""
Main application file.
Add and implement entry points here (We could move them out later if desired.)
"""

# Flask
from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import random

# For hashing
from werkzeug.security import generate_password_hash, check_password_hash

# Others
import yaml

# App, db and tables
from init_schema import app, db, User, Group, group_member_table, Content, List, Rating

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

# Return current user
def whoami():
    if not logged_in():
        return None
    return User.query.filter_by(user_id=session['uid']).first()

def is_user(user_name):
    if not logged_in():
        return False
    
    return whoami_username() == user_name

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
/create_group/
/group/<group_name>/join
/group/<group_name>/leave
/group/<group_name>/edit
/group/<group_name>
/search_group/
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
    return render_template("index.html")

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
        return redirect('/')

    # Get all groups the user is in
    user_groups = user.get_all_groups()\
                    .order_by(Group.name)\
                    .all()

    is_owner = whoami_username() == user.username

    return render_template('user.html', user=user, groups=user_groups, is_owner=is_owner)

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
        new_group = Group(name=group_name)
    
        # Save changes
        db.session.add(new_group)
        
        # # Add current user to the newly created group
        # new_group.add_member(whoami())

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
        group.members.remove(user)
        group.size -= 1
        db.session.commit()
        
        # Group has no members, disband.
        if group.size <= 0:
            
            # Clear list ( so all foreign keys are let-go )
            group.lists = []
            
            # Delete the group
            group_q.delete()
            
            db.session.commit()
            flash('Group disbanded!', 'success')
            return redirect('/')

        flash('Successfully left group!', 'success')

        return redirect(url_for('group', group=group))
    
    # We're trying to leave, but we
    # are not in the group
    flash('Not in group!', 'danger')
    return redirect(url_for('group', group=group))

@app.route('/group/<group_name>/edit')
def edit_group(group_name, methods=['GET', 'POST']):
    group = Group.query.filter_by(name=group_name).first()
    if group is None:
        flash("Group not found", 'danger')
        return redirect('/')
    
    # Get list of all members
    members_q = group.get_all_members()
    members = group.get_all_members().all()

    who = whoami()
    is_owner = who == group.owner_id
    is_member = members_q.filter(User.user_id == who.user_id).first()
    if request.method == 'GET':
        if not logged_in():
            session['last_page'] = url_for('edit_group', group_name=group.name)
            return redirect(url_for('signin'))
            
        return render_template('edit_group.html', group=group, members=members, is_member=is_member, is_owner=is_owner)
    elif request.method == 'POST':
        gid = group.group_id
        form = request.form
        group_name = form['group_name'] if is_owner else group.name
        group_img = form['group_img']
        group_info = form['group_info']

        if group_name  == "":
            flash('Group name cannot be empty', 'danger')
            return redirect(url_for('edit_group',group=group, members=members, is_member=is_member, is_owner=is_owner))
            
        if group_img == "":
            group_img = '/static/place_holder_img.png';

        if group_info == "":
            group_info = Group.set_default_info
                
        # existing group name
        existing_name = Group.query.filter(Group.name == group_name).first()
        if existing_name and existing_name.name != group.name:
            flash('This name has already been taken', 'danger')
            return redirect(url_for('edit_group', group=group, members=members, is_member=is_member, is_owner=is_owner))
                
        # Update group    
        group_update = Group.query.filter(Group.content_id == gid).first()
        group_update.name = group_name
        group_update.info = group_info
        group_update.group_img = group_img
        db.session.commit()
            
        # Success message
        flash('Group edited successfully', 'success')

    return redirect(url_for('group', group=group))


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

# Search Group
@app.route('/search_group/', methods=['GET', 'POST'])
def search_group():
    if request.method == 'GET':
        return render_template('search_group.html')
    elif request.method == 'POST':

        group_name = request.form['group_name']
        search_name = "%{}%".format(group_name)
        groups = Group.query.filter(Group.name.like(search_name)).order_by(Group.name).all()
        
        return render_template('search_group.html', groups=groups)
    
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
        found = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        if found:
            flash('Content already exist', 'danger')
            return redirect('/create_content/')
            
        # Make new content
        new_content = Content(content_title, content_type)
        db.session.add(new_content)
        db.session.commit()
        
        # Success message
        flash('Content added successfully', 'success')
   
        return redirect(url_for('content', content_title=content_title, content_type=content_type))
    
    return render_template('create_content.html')
    
@app.route('/content/<content_type>/<content_title>', methods=['GET','POST'])
def content(content_type, content_title):
    if request.method == 'GET':
        found = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        
        if found:
            content_title = found.title
            content_type = found.content_type
        
            return render_template('content.html', content=found)
        else:
            flash('Content page not found', 'danger')
            return redirect('/')
    
    elif request.method == 'POST':
        return redirect(url_for('edit_content',content_type=content_type, content_title=content_title))

# Search for content by title
    
@app.route('/content/search/', methods=['GET', 'POST'])
def search_content():
    if request.method == 'GET':
        return render_template('search_content.html')
    elif request.method == 'POST':
        
        content_title = request.form['content_title']
        search_name = "%{}%".format(content_title)
        contents = Content.query.filter(Content.title.like(search_name)).order_by(Content.title).all()
        return render_template('search_content.html', contents=contents)
    return render_template('search_content.html')

@app.route('/content/<content_type>/<content_title>/edit', methods=['GET', 'POST'])
def edit_content(content_type, content_title):
    if request.method == 'GET':
        found = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        if found:
            content_title = found.title
            content_type = found.content_type
        
        if not logged_in():
            session['last_page'] = url_for('edit_content',content_type=content_type, content_title=content_title)
            return redirect(url_for('signin'))
        
        return render_template('edit_content.html',content=found)

    elif request.method == 'POST':
        content = Content.query.filter((Content.title==content_title) & (Content.content_type == content_type)).first()
        cid = content.content_id
        form = request.form
        content_title = form['content_title']
        content_img = form['content_img']
        content_synopsis = form['content_synopsis']


        
        # TODO make sure form results are acceptable and save them

        # blank input
        if content_title == "":
            flash('Content title can not be empty', 'danger')
            return redirect(url_for('edit_content',content_type=content_type, content_title=content_title))
        
        if content_img == "":
            content_img = '/static/place_holder_img.png';

        if content_synopsis == "":
                content_synopsis = 'No sypnosis has been provided.'
            
        # existing content
        found = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        if found:
            if found.title != content_title:
                flash('This content has its own page already', 'danger')
                return redirect(url_for('edit_content',content_type=content_type, content_title=content_title))
            
        # Update content    
        content = Content.query.filter(Content.content_id == cid).first()
        content.title = content_title
        content.synopsis = content_synopsis
        content.poster = content_img
        db.session.commit()
        
        # Success message
        flash('Content edited successfully', 'success')
   
        return redirect(url_for('content', content_title=content_title, content_type=content_type))


@app.route('/content/<content_type>/<content_title>/me/add', methods=['GET'])
def list_add_content(content_type, content_title):
    
    # Handle login
    if not logged_in():
        session['last_page'] = url_for('list_add_content', content_type=content_type, content_title=content_title)
        return redirect(url_for('signin'))
    
    user = whoami()
    content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
    
    if content:
        if not user.lists[List.WATCH_LIST].has_content(content):
            flash(f'Added to watch list', 'success')
            user.lists[List.WATCH_LIST].add(content)
            db.session.commit()
        else:
            flash(f'Content already in list', 'danger')
            
    else:
        flash(f'Action failed', 'danger')
        
    return redirect(url_for('content', content_title=content_title, content_type=content_type))

@app.route('/content/<content_type>/<content_title>/<group_id>/add', methods=['GET'])
def group_list_add_content(content_type, content_title, group_id):
    
    # Handle login
    if not logged_in():
        session['last_page'] = url_for('group_list_add_content', content_type=content_type, content_title=content_title, group_id=group_id)
        return redirect(url_for('signin'))
    
    print('GPID', group_id)
    group = Group.query.filter_by(group_id = group_id).first()
    content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
    
    if content:
        if not group.lists[List.WATCH_LIST].has_content(content):
            flash(f'Content successfully added to {group.name}\'s watch list', 'success')
            group.lists[List.WATCH_LIST].add(content)
            db.session.commit()
        else:
            flash(f'Content already in list', 'danger')
            
    else:
        flash(f'Action failed', 'danger')
        
    return redirect(url_for('content', content_title=content_title, content_type=content_type))
    
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
        is_owner = is_user(owner_name) or ((list_owner.has_member(whoami().user_id) != None) if user is not None else False) 
    
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
    
@app.route("/content/<content_type>/<content_title>/modal/", methods=['GET', 'POST'])
def list_add_modal(content_type, content_title):
    if request.method == 'GET':
        
        
        # Handle login
        if not logged_in():
            session['last_page'] = url_for('list_add_modal', content_type=content_type, content_title=content_title)
            return redirect(url_for('signin'))
        
        found = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        
        if found:
            
            user_groups = whoami().get_all_groups()\
                    .order_by(Group.name)\
                    .all()
            
            return render_template('list_add_modal.html', content=found, groups=user_groups)
        else:
            flash('Content page not found', 'danger')
            return redirect('/')
    
    elif request.method == 'POST':
        return redirect(url_for('edit_content',content_type=content_type, content_title=content_title))

@app.route('/content/<content_type>/<content_title>/rate', methods=['GET','POST'])
def rate_content(content_type, content_title):
    if request.method == 'GET':
        # Handle login
        if not logged_in():
            session['last_page'] = url_for('content', content_type=content_type, content_title=content_title)
            return redirect(url_for('signin'))
        
        content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        if content:
            return render_template('set_rating_modal.html',content=content)
        else:
            return render_template('content', content_type=content_type, content_title=content_title)
        
    elif request.method == 'POST':  
        
        if not logged_in():
            session['last_page'] = url_for('content', content_type=content_type, content_title=content_title)
            return redirect(url_for('signin'))

        user = whoami()
        content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        rating = request.form["slider"]
        
        if content:
            action = content.set_rating(user.user_id, rating)
            
            if action == Rating.ADDED_RATING:
                flash('Rating added', 'success')
            elif action == Rating.EDITTED_RATING:
                flash('Rating editted', 'success')
            
            db.session.commit()
            return redirect( url_for('content', content_type=content_type, content_title=content_title))
                
        flash('no content found', 'danger')
        return redirect('/')

@app.route("/content/<content_type>/<content_title>/rate_modal/", methods=['GET', 'POST'])
def set_rating_modal(content_type, content_title):
    if request.method == 'GET':
        #content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        return redirect(url_for('rate_content',content_type=content_type, content_title=content_title))
    
    if request.method == 'POST':
        #content = Content.query.filter((Content.title == content_title) & (Content.content_type == content_type)).first()
        return redirect(url_for('rate_content',content_type=content_type, content_title=content_title))

#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#

# Main program entry point
if __name__ == '__main__':  
    app.run(debug=True)



