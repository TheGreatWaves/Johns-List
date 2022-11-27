"""
Main application file.
Add and implement entry points here (We could move them out later if desired.)
"""

# Flask
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# For hashing
from werkzeug.security import generate_password_hash, check_password_hash

# Others
import yaml

# App, db and tables
from init_schema import app, db, user

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
        
        new_user = user(email=email, username=username, password=hashed_pw)
        
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
        found = user.query.filter_by(email=user_email).first()
        
        # Try finding
        if found is not None:
            
            # Found, check password
            if check_password_hash(found.password, loginForm['password']):
                flash("Log In successful",'success')
                return redirect('/')
            else:
                flash("Incorrect credentials", 'danger')
                return render_template('signin.html')
        else:
            flash('User not found', 'danger')
            return render_template('signin.html')
    
    return render_template('signin.html')


#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#

# Main program entry point
if __name__ == '__main__':  
    app.run(debug=True)



