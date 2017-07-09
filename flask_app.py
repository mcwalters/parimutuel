
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

class BankRoll(db.Model):
    __tablename__ = "bank"
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(4096))
    password = db.Column(db.String(4096))
    balance = db.Column(db.Numeric(13,2))

class Race(db.Model):
    __tablename__ = "races"
    id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String(4096))
    in_progress = db.Column(db.Boolean())

class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.String(4096))
    bettor = db.Column(db.String(4096))
    bet = db.Column(db.Numeric(13,2))


@app.route('/bets')
def bet_list():
    return render_template('bets.html',tables=[pd.read_sql_query('select * from bank;',db.engine).to_html()],
                           titles = ['na', 'Female surfers', 'Male surfers'])

@app.route('/races')
def race_list():
    return render_template('bets.html',tables=[pd.read_sql_query('select * from races where in_progress;',db.engine).to_html()],
                           titles = ['na', 'Female surfers', 'Male surfers'])

# route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        owner = request.form['username']
        password = request.form['password']
        if BankRoll.query.filter_by(owner=owner).first():
            if BankRoll.query.filter_by(owner=owner,password=password).first():
                session['logged_in'] = True
                return redirect('/bets')
            else:
                error = 'Wrong password. Please try again.'
                return render_template('login.html', error=error)
        else:
            new_bettor = BankRoll(owner=request.form["username"],
                                  password=request.form["password"],
                                  balance=100)
            db.session.add(new_bettor)
            db.session.commit()
            return redirect('/races')
    return render_template('login.html', error=error)


# For development to reset the database
#db.drop_all()
#db.create_all()
