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

# Load credentials
cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)

# Intialize flask app
app = Flask(__name__)

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

# Connect app's db to SQLAlchemy
db = SQLAlchemy(app)

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
        
        p1 = userDetails['email']
        p2 = userDetails['username']
        p3 = userDetails['password']
        
        hashed_pw = generate_password_hash(p3)
        
        flash('Successfully registered.', 'success')
        return redirect('/')    
    return render_template('signup.html')

#=========================================#
#    END OF ENTRY POINT INITIALIZATION    #
#=========================================#

# Main program entry point
if __name__ == '__main__':  
    app.run(debug=True)



