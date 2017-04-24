
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)

app.secret_key = os.urandom(12)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="mcwalters",
    password="foobarFuzzy",
    hostname="mcwalters.mysql.pythonanywhere-services.com",
    databasename="mcwalters$parimutuel",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))

class BankRoll(db.Model):
    __tablename__ = "bank"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(4096))
    balance = db.Column(db.Numeric(13,2))

class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)
    bettor = db.Column(db.String(4096))
    in_progress = db.Column(db.Boolean())
    bet = db.Column(db.Numeric(13,2))

@app.route('/')
def hello_world():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('bets.html',tables=[pd.read_sql_query('select * from comments;',db.engine).to_html()],
                           titles = ['na', 'Female surfers', 'Male surfers'])

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            comment = Comment(content=request.form["username"])
            db.session.add(comment)
            db.session.commit()
        else:
            session['logged_in'] = True
            return redirect('/')
    return render_template('login.html', error=error)
