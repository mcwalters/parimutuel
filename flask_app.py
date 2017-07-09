
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
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

class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.String(4096))
    bettor = db.Column(db.String(4096))
    candidate = db.Column(db.String(4096))
    bet = db.Column(db.Numeric(13,2))
    payout = db.Column(db.Numeric(13,2))


class Race(db.Model):
    __tablename__ = "races"
    id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String(4096))
    owner = db.Column(db.String(4096))
    in_progress = db.Column(db.Boolean())

    def __repr__(self):
        return self.race_name


@app.route('/races', methods=['GET', 'POST'])
def race_list():
    if request.method == 'POST':
        if not session['logged_in']:
            return redirect('/')
        new_race = Race(race_name = request.form['race_name'],
                        in_progress = True,
                        owner = session['Bettor'])
        db.session.add(new_race)
        db.session.commit()
        return redirect('/races/'+request.form['race_name'])

    return render_template('races.html',tables=Race.query.filter_by(in_progress=True),
                            titles = ['na','Races open for betting'])

@app.route('/races/<race_name>/results/<winner>', methods=['GET', 'POST'])
def payout(race_name,winner):

    return


@app.route('/races/<race_name>/results', methods=['GET', 'POST'])
def race_results(race_name):
    Race.query.filter_by(race_name=race_name).first().in_progress = False
    db.session.commit()

    odds_query = """select candidate, odds from candidate_odds
                    where race = '{race}' """.format(race=race_name)
    odds = pd.read_sql_query(odds_query,db.engine)
    return render_template('results.html', tables=[x for x in odds.itertuples()],
                           titles = ['na', 'Odds places'],
                           owner = True if Race.query.filter_by(owner=session['Bettor'],
                                                                race_name=race_name).first() else False)

@app.route('/races/<race_name>', methods=['GET', 'POST'])
def race_odds(race_name):
    if not session['logged_in']:
        return redirect('/')

    if request.method == 'POST':
        new_bet = Bet(candidate = request.form['candidate'],
                  bet = request.form['bet'],
                  bettor = session['Bettor'],
                  race = race_name)
        db.session.add(new_bet)
        bettor = BankRoll.query.filter_by(owner=session['Bettor']).first()
        bettor.balance = bettor.balance - Decimal(request.form['bet'])
        db.session.commit()
        return redirect('/races/' + race_name)

    if Race.query.filter_by(race_name=race_name).first():
        odds_query = """select candidate, odds from candidate_odds
                        where race = '{race}' """.format(race=race_name)

        odds = pd.read_sql_query(odds_query,db.engine)

        return render_template('bets.html', tables=[x for x in odds.itertuples()],
                               titles = ['na', 'Odds places'],
                               race_name=race_name,
                               owner = True if Race.query.filter_by(owner=session['Bettor'],
                                                                    race_name=race_name).first() else False)
    else:
        return redirect('/races')

@app.route('/races/<race_name>/<candidate>', methods=['GET', 'POST'])
def place_bet(race_name, candidate):
    if not session['logged_in']:
        return redirect('/')

    if request.method == 'POST':
        new_bet = Bet(candidate = candidate,
                  bet = request.form['bet'],
                  bettor = session['Bettor'],
                  race = race_name)
        db.session.add(new_bet)
        bettor = BankRoll.query.filter_by(owner=session['Bettor']).first()
        bettor.balance = bettor.balance - Decimal(request.form['bet'])
        db.session.commit()
        return redirect('/races/' + race_name)

    return render_template('candidate_bet.html',
                           race_name=race_name,
                           candidate=candidate,
                           owner = True if Race.query.filter_by(owner=session['Bettor'],
                                                                race_name=race_name).first() else False)



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
                session['Bettor'] = owner
                return redirect('/races')
            else:
                error = 'Wrong password. Please try again.'
                return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            session['Bettor'] = owner
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
