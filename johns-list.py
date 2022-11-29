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
            flash('Password does not match.', 'danger')
            return render_template('signup.html')
        
        email = userDetails['email']
        username = userDetails['username']
        pw = userDetails['password']
        
        hashed_pw = generate_password_hash(pw)
        
        # TODO: Ensure that the new user isn't using an existing email!
        new_user = User(email=email, username=username, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Successfully registered.', 'success')
        return redirect('/')    
    return render_template('signup.html')

# Sign in
@app.route("/signin/", methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        loginForm = request.form
        user_email = loginForm['email']
        
        # Query for user entry
        found = User.query.filter_by(email=user_email).first()
        
        # Try finding
        if found is not None:
            
            # Found, check password
            if check_password_hash(found.password, loginForm['password']):

                # Log session info
                session['login'] = True
                session['username'] = found.username


                flash('Welcome ' + session['username'] + '.','success')
                return redirect('/')
            else:
                flash("Incorrect credentials", 'danger')
                return render_template('signin.html')
        else:
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

    if user is None:
        flash("User not found", 'danger')
        return redirect('/')

    user_groups = Group.query.join(group_member_table).join(User).filter((group_member_table.c.member_id == User.user_id) & (group_member_table.c.group_id == Group.group_id)).filter(User.user_id == user.user_id).order_by(Group.name).all()



    return render_template('profile.html', user=user, groups=user_groups, is_owner = (session['username'] == user.username))

@app.route('/create_group/', methods=['GET', 'POST'])
def create_group():
    if request.method == 'GET':
        return render_template('create_group.html')
    elif request.method == 'POST':

        group_form = request.form

        group_name = group_form['group_name']

        new_group = Group(name=group_name)
        user = User.query.filter_by(username=session['username']).first()

        new_group.members.append(user)

        db.session.add(new_group)
        db.session.commit()

        flash(f'New group [{group_name}] successfully created!', 'success')
        return redirect('/profile/' + session['username'])
    else:
        return render_template('create_group.html')

# Join Group
@app.route('/group/<group_name>/join')
def join_group(group_name):
    
    group = Group.query.filter_by(name=group_name).first()
    user = User.query.filter_by(username=session['username']).first()

    in_group = Group.query.join(group_member_table).join(User).filter((group_member_table.c.member_id == user.user_id) & (group_member_table.c.group_id == group.group_id)).first()

    if in_group is not None:
        flash('Already in group!', 'danger')
        return redirect('/')

    group.members.append(user)
    db.session.commit()

    flash('Joined group!', 'success')

    # TODO: Redirect back to the group page!
    return redirect('/')

# Group
@app.route('/group/<group_name>', methods=['GET'])
def group(group_name):

    # Find user using username
    group = Group.query.filter_by(name = group_name).first()

    if group is None:
        flash("Group not found", 'danger')
        return redirect('/')

    members = User.query.join(group_member_table).join(Group).filter((group_member_table.c.member_id == User.user_id) & (group_member_table.c.group_id == Group.group_id)).filter(Group.group_id == group.group_id).all()

    return render_template('group.html', group=group, members=members)

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



