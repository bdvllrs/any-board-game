import json
import traceback
import uuid

from flask import Flask, request, make_response
from flask_sockets import Sockets

from game_engine.games.bataille.main import BatailleGame
from game_engine.players import Player

app = Flask(__name__)
sockets = Sockets(app)
games = dict()
game_creators = dict()


def generate_username():
    # TODO: funnier user names
    return uuid.uuid4().hex[:15]


def get_query_string_fields(query_string):
    fields = dict()
    for query in query_string.split(","):
        key, value = query.split('=')
        fields[key] = value
    return fields


@sockets.route("/round/<string:round_id>/join")
def join_round_socket(ws, round_id):
    query = get_query_string_fields(ws.environ['QUERY_STRING'])
    if 'playerId' not in query:
        ws.send(json.dumps({"status": 403, "message": "PlayerId is required."}))
        ws.close()
        return

    player_id = query['playerId']

    if round_id not in games.keys():
        ws.send(json.dumps({"status": 403, "message": "RoundId is incorrect."}))
        ws.close()
        return

    game = games[round_id]

    if player_id not in map(lambda u: u.uid, game.players):
        ws.send(json.dumps({"status": 403, "message": "Player has not joined the game."}))
        ws.close()
        return

    player = game.players[player_id]
    player.socket = ws

    while not ws.closed:
        # Listen for client messages
        response = ws.receive()
        response = json.loads(response)
        if response is not None:
            player.receive(response)


def add_player_to_round(round_id, username):
    if username is None:
        username = generate_username()
    if round_id not in games.keys():
        return make_response({}, 404)

    game = games[round_id]

    if game.started:
        return make_response({"message": "Game has already started."}, 403)
    if username in map(lambda u: u.username, game.players.values()):
        return make_response({"message": f"Username {username} already exists."}, 403)
    player_id = uuid.uuid4().hex
    player = Player(username, player_id)
    is_added = game.add_player(player)
    if not is_added:
        return make_response({"message": f"You cannot enter the game."}, 403)
    return {"playerId": player_id,
            "id": round_id,
            "gameId": game.game_id,
            "status": "pending",
            "createdOn": game.created_on,
            "createdBy": game.created_by,
            "minPlayers": game.min_players,
            "maxPlayers": game.max_players,
            "public": game.is_public,
            "players": list(map(lambda u: u.username, game.players.values()))}


@app.route('/round/create/<string:game_id>', methods=['POST'])
def start_game(game_id):
    form = dict(request.form)
    if 'username' not in form:
        form['username'] = generate_username()
    if 'public' not in form:
        form['public'] = False
    creator_username = form['username']
    is_game_public = form['public']  # TODO: public games
    is_game_public = False
    round_id = uuid.uuid4().hex
    # TODO: automatically load all games in the folder
    if game_id == "bataille":
        try:
            games[round_id] = BatailleGame(round_id, creator_username, is_game_public)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            return make_response({"message": "An unexpected error has occurred."}, 500)
    else:
        return make_response({"message": "Game does not exists."}, 404)
    game_creators[round_id] = creator_username
    return add_player_to_round(round_id, creator_username)


@app.route("/round/<string:round_id>/join", methods=['GET'])
def join_game(round_id):
    username = request.args.get('username', None)
    return add_player_to_round(round_id, username)


if __name__ == '__main__':
    import argparse
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", default=5000, help="Port of the server.")
    args = parser.parse_args()

    server = pywsgi.WSGIServer(('', args.port), app, handler_class=WebSocketHandler)
    server.serve_forever()
