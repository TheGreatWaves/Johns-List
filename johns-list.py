from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
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
mysql = MySQL(app)

# Entry points 
# Note: Make sure entry points are defined above main.

# Index
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        userDetails = request.form
        p1 = userDetails['email']
        p2 = userDetails['username']
        p3 = userDetails['password']
        return redirect('/')    
    return render_template('signup.html')

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)



