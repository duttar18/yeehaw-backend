import os
import json
import flask
import flask_cors
import flask_sqlalchemy
import time
import random
from datetime import datetime

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
db = SQLAlchemy(app)
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
    time1 = db.Column(db.Float,default=0)
    time2 = db.Column(db.Float,default=0)
    waittime = db.Column(db.Integer)
    live = db.Column(db.Boolean,default=True)

    def __init__(self,id1):
        self.id1=id1
        self.waittime=random.randint(1000,5000)

@app.route('/finding',methods=["POST"])
@cross_origin()
def finding():
    body = flask.request.get_json()
    game = Games.query.filter_by(id2=None).first()
    otherid = 0

    # if you dont find game
    if not game:
        game = Games(body["id"])
        db.session.add(game)
        db.session.commit()
        id=game.id
        while not game.id2:
            db.session.refresh(game) # change if time
            game = Games.query.filter_by(id=id).first()
        otherid=game.id2
    
    # if you find a game
    else:
        game.id2=body["id"]
        db.session.commit()
        otherid=game.id1


    otherplayer = Players.query.filter_by(id=otherid).first()

    player = Players.query.filter_by(id=body["id"]).first()

    return flask.jsonify(
        playerMoney = player.money,
        player2Money = otherplayer.money,
        player2Name = otherplayer.name,
        waittime = game.waittime,
        gameId = game.id
    )

@app.route('/deathmatch',methods=["POST"])
@cross_origin()
def deathmatch():
    body = flask.request.get_json()

    game = Games.query.filter_by(body["gameId"])

    if game.id1==body['id']:
        game.time1=body["time"]
    else:
        game.time2=body["time"]
    db.session.commit()



    # wait till both sides respond
    start = datetime.now()
    while (not (game.time1 and game.time2)) and ((datetime.now()-start).total_seconds()<2):
        db.session.refresh()
        game = Games.query.filter_by(body["gameId"])
        if game.time1 and game.time2:
            game.live=False
        time.sleep(0.25)
    game.live=False
    db.session.commit()
    
    # figure out who won
    won = True
    if game.id1==body['id']:
        if game.time2 and game.time2<game.time1:
            won=False
    else:
        if game.time1 and game.time1<game.time2:
            won=False


    player2Time = 0
    enemyId = 0
    if game.id1==body['id']:
        player2Time=game.time2
        enemyId=game.id2
    else:
        player2Time=game.time1
        enemyId=game.id1
    
    player = Players.query.filter_by(id=body["id"])
    enemy = Players.query.filter_by(id=enemyId)
    
    if won:
        money = int(enemy.money*0.1)

        player.money += money
        enemy.money -=money
    else:
        money = int(player.money*0.1)

        enemy.money += money
        player.money -= money
    db.session.commit()

    return flask.jsonify(
        won=won,
        player2Time = player2Time,
        money=player.money,
        player2Money=enemy.money
    )

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

