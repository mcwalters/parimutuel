
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, request
from flask.ext.mysql import MySQL

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="mcwalters",
    password="Fuzzy",
    hostname="mcwalters.mysql.pythonanywhere-services.com",
    databasename="mcwalters$parimutuel",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

@app.route('/')
def hello_world():
    return 'Hello from Flaskeresque!'

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/')
    return render_template('login.html', error=error)

