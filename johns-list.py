"""
Main application file.
Add and implement entry points here (We could move them out later if desired.)
"""

# Flask
from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy

# For hashing
from werkzeug.security import generate_password_hash, check_password_hash

# Others
import yaml

# App, db and tables
from init_schema import app, db, User, Group, group_member_table

# Load credentials
cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)


# Database credentials configurations 
app.config['MYSQL_HOST'] = cred['mysql_host']
app.config['MYSQL_USER'] = cred['mysql_user']
app.config['MYSQL_PASSWORD'] = cred['mysql_password']
app.config['MYSQL_DB'] = cred['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'SECRET_KEY' # TODO: REMOVE THIS!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:johnpass@localhost:13310/johndb'

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
    return User.query.filter_by(username=session['username']).first()

#=========================================#
# INITILIAZE ENTRY POINTS BELOW THIS LINE #
#=========================================#

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
    if request.method == 'GET':
        return render_template('signup.html')

    elif request.method == 'POST':
        userDetails = request.form
        
        # Check that passwords matches
        if userDetails['password'] != userDetails['confirm_password']:
            flash('Password does not match', 'danger')
            return render_template('signup.html')
        
        email = userDetails['email']
        username = userDetails['username']

        if email == "":
            flash('Email can not be blank', 'danger')
            return render_template('signup.html')

        if username == "":
            flash('Username can not be blank', 'danger')
            return render_template('signup.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

        # If user already exists...
        if existing_user:

            # Note: elif is used to prevent bombarding with flush

            # Email is in use
            if existing_user.email == email:
                flash('Email already in use', 'danger')
            # Usernname is in use
            elif existing_user.username == username:
                flash('Username unavailable', 'danger')
            
            return render_template('signup.html')
    

        pw = userDetails['password']
        hashed_pw = generate_password_hash(pw)
        
        new_user = User(email=email, username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Successfully registered', 'success')

        # Redirect user to sign in page upon success
        return redirect('/signin/')    

    return render_template('signup.html')

# Sign in
@app.route("/signin/", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        
        # Safe guard
        if logged_in():
            return redirect('/')

        return render_template('signin.html')

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
                return render_template('signin.html')

        else:
            # No existing user with given email/username
            flash('User not found', 'danger')
            return render_template('signin.html')
    
    return render_template('signin.html')

# Sign out
@app.route('/signout/')
def signout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

# User profile page
@app.route('/profile/<username>', methods=['GET'])
def profile(username):

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

    return render_template('profile.html', user=user, groups=user_groups, is_owner=is_owner)

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
            return redirect('/create_group/')

        found = Group.query.filter_by(name=group_name).first()
       
        # If found, group name has been taken
        if found:
            flash('Group name already taken', 'danger')
            return redirect('/create_group/')

        # Create the new group
        new_group = Group(name=group_name)
    
        # Add current user to the newly created group
        new_group.members.append(whoami())

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

    group.members.append(user)
    group.size += 1
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
            group_q.delete()
            db.session.commit()
            flash('Group disbanded!', 'success')
            return redirect('/')

        flash('Successfully left group!', 'success')

        return redirect(url_for('group', group_name=group_name))
    
    # We're trying to leave, but we
    # are not in the group
    flash('Not in group!', 'danger')
    return redirect(url_for('group', group_name=group_name))

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
    
#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#

# Main program entry point
if __name__ == '__main__':  
    app.run(debug=True)



