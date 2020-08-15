import os
import json
import flask
import flask_cors
import flask_sqlalchemy
import datetime

from flask import Flask, request, jsonify, session,make_response, current_app, render_template, json
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

# initializes app
app = Flask(__name__)


# initializes database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config.from_object(__name__)

app.config['SECRET_KEY'] = 'yosafdyousfodjasodkj'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

class Players(db.Model):
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    money = db.Column(db.Integer, default=50)
    def __init__(self,name):
        self.name=name
class Games(db.Model):
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    id1 = db.Column(db.Integer)
    id2 = db.Column(db.Integer)
    time1 = db.Column(db.Integer)
    time2 = db.Column(db.Integer)
    waittime = db.Column(db.Integer)
    live = db.Column(db.Boolean,default=True)

    def __init__(self,id1):
        self.id1=id1
        self.waittime=random.randint(1000,5000)

@app.route('/find',methods=["POST"])

    body = flask.request.get_json()
    game = Games.query.filter_by(id2=None).first()
    otherid = 0

    # if you dont find game
    if not game:
        game = Games(body["id"])
        db.session.add(game)
        db.session.commit()
        while not game.id2:
            db.session.refresh() # change if time
            game = Games.query.filter_by(id1=body["id"],live=True).filter(Games.id2!=None).first()
        otherid=game.id2
    
    # if you find a game
    else:
        game.id2=body["id"]
        db.session.commit()
        otherid=game.id1


    otherplayer = Players.query.filter_by(id=otherid).first()

    player = Players.query.filter_by(id=body["id"]).first()

    return flask.jsonify(
        player = player.money
        player2Money = otherplayer.money
        player2Name = otherplayer.name
        waittime = game.waittime
    )

@app.route('/finding',methods=["POST"])
def finding():
    body = flask.request.get_json()

@app.route("/createPlayer",methods=["POST"]) 
@cross_origin()
def createPlayer():
    body = flask.request.get_json()
    player = Players(body["name"])
    db.session.add(player)
    db.session.commit()

    return flask.jsonify(
        id=player.id,
        name=player.name
    )

