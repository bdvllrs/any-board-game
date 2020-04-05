import uuid
from typing import Dict

from flask import Flask, request
import flask_socketio as sio

from game_engine.game import GameInstance
from game_engine.players import Player
from games.bataille.main import BatailleInstance

app = Flask(__name__)
socketio = sio.SocketIO(app)
games: Dict[GameInstance] = dict()


@app.route('/create', methods=['POST'])
def start_game():
    game_name = request.form['game']
    game_id = uuid.uuid4().hex
    if game_name == "bataille":
        games[game_id] = BatailleInstance(game_id)
    else:
        return {"error": True,
                "message": f"No game named {game_name}."}
    return {"game_id": game_id,
            "error": False}


@app.route("/join", methods=['POST'])
def join_game():
    game_id = request.form['game_id']
    username = request.form['username']
    socket_id = request.form['socket_id']
    if game_id not in games.keys():
        return {"error": True,
                "message": f"Game {game_id} does not exist."}
    if games[game_id].started:
        return {"error": True,
                "message": f"Game has already started."}
    if username in map(lambda u: u.username, games[game_id].get_players()):
        return {"error": True,
                "message": f"Username {username} already exists."}
    player_id = uuid.uuid4().hex
    player = Player(username, player_id, socket_id)
    games[game_id].add_player(player)
    sio.join_room(game_id, socket_id)
    sio.emit("new-player", dict(username=player.username), room=game_id)
    # TODO: Give information about states
    return {"error": False,
            "message": "",
            "player_id": player_id,
            "players": list(map(lambda u: u.username, games[game_id].get_players()))}


@app.route("/start", methods=['POST'])
def start_game():
    game_id = request.form['game_id']
    player_id = request.form['player_id']
    if game_id not in games.keys():
        return {"error": True,
                "message": f"Game {game_id} does not exist."}
    if games[game_id].started:
        return {"error": True,
                "message": f"Game has already started."}
    if player_id not in map(lambda u: u.uid, games[game_id].get_players()):
        return {"error": True,
                "message": f"Player {player_id} is not in the game."}

    games[game_id].start()
    player = games[game_id].get_players([player_id])[0]
    sio.emit("start", dict(username=player.username), room=game_id)
    games[game_id].next()


@app.route("/play", methods=['POST'])
def play():
    game_id = request.form['game_id']
    player_id = request.form['player_id']
    if game_id not in games.keys():
        return {"error": True,
                "message": f"Game {game_id} does not exist."}
    if not games[game_id].started:
        return {"error": True,
                "message": f"Game has not started yet."}
    if player_id not in map(lambda u: u.uid, games[game_id].get_players()):
        return {"error": True,
                "message": f"Player {player_id} is not in the game."}
    # TODO: Check that user can play
