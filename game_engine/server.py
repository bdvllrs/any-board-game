import datetime
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
    if player_id not in map(lambda u: u.uid, games[round_id]['game'].players):
        ws.send(json.dumps({"status": 403, "message": "Player has not joined the game."}))
        ws.close()
        return

    player = games[round_id]['game'].players[player_id]
    sent_messages = {}

    while not ws.closed:
        # Send to client
        message = player.get_message()
        if message is not None:
            message_content = dict(id=uuid.uuid4().hex,
                                   content=message['content'])
            ws.send(message_content)
            sent_messages[message_content['id']] = message
        # Listen for client response
        response = ws.receive()
        response = json.loads(response)
        if response is not None and 'origin' in response and 'content' in response:
            if response['origin'] == "$CHAT":
                for player in games[round_id]['game'].players:
                    if player.uid != player_id:
                        player.send(response['content'])
            if response['origin'] in sent_messages:
                message = sent_messages[response['origin']]
                if message['callback'] is not None:
                    message['callback'](response['content'])
                del sent_messages[response['origin']]


def add_player_to_round(round_id, username):
    if username is None:
        username = generate_username()
    if round_id not in games.keys():
        return make_response({}, 404)
    if games[round_id]['game'].started:
        return make_response({"message": "Game has already started."}, 403)
    if username in map(lambda u: u.username, games[round_id]['game'].players.values()):
        return make_response({"message": f"Username {username} already exists."}, 403)
    player_id = uuid.uuid4().hex
    player = Player(username, player_id)
    is_added = games[round_id]['game'].add_player(player)
    if not is_added:
        return make_response({"message": f"You cannot enter the game."}, 403)
    return {"playerId": player_id,
            "id": round_id,
            "gameId": games[round_id]['gameId'],
            "status": "pending",
            "createdOn": games[round_id]['createdOn'],
            "createdBy": games[round_id]['createdBy'],
            "minPlayers": 0,
            "maxPlayers": 0,
            "public": games[round_id]['public'],
            "players": list(map(lambda u: u.username, games[round_id]['game'].players.values()))}


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
    if game_id == "bataille":
        try:
            games[round_id] = {"game": BatailleGame(round_id),
                               "createdOn": datetime.datetime.now(),
                               "createdBy": creator_username,
                               "public": is_game_public,
                               "gameId": game_id}
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            return make_response({"message": "An enexpected error has occured."}, 500)
    else:
        return make_response({"message": "Game does not exists."}, 404)
    game_creators[round_id] = creator_username
    return add_player_to_round(round_id, creator_username)


@app.route("/round/<string:round_id>/join", methods=['GET'])
def join_game(round_id):
    username = request.args.get('username', None)
    return add_player_to_round(round_id, username)


# @app.route("/start", methods=['POST'])
# def start_game():
#     game_id = request.form['game_id']
#     player_id = request.form['player_id']
#     if game_id not in games.keys():
#         return {"error": True,
#                 "message": f"Game {game_id} does not exist."}
#     if games[game_id].started:
#         return {"error": True,
#                 "message": f"Game has already started."}
#     if player_id not in map(lambda u: u.uid, games[game_id].get_players()):
#         return {"error": True,
#                 "message": f"Player {player_id} is not in the game."}
#
#     games[game_id].start()
#     player = games[game_id].get_players([player_id])[0]
#     sio.emit("start", dict(username=player.username), room=game_id)
#     current_state = games[game_id].next()
#
#     return {"message": current_state.status,
#             "error": current_state.error,
#             "current_node_state": current_state.name}
#
#
# @app.route("/play", methods=['POST'])
# def play():
#     game_id = request.form['game_id']
#     player_id = request.form['player_id']
#     message = request.form['message']
#     if game_id not in games.keys():
#         return {"error": True,
#                 "message": f"Game {game_id} does not exist."}
#     if not games[game_id].started:
#         return {"error": True,
#                 "message": f"Game has not started yet."}
#     if player_id not in map(lambda u: u.uid, games[game_id].get_players()):
#         return {"error": True,
#                 "message": f"Player {player_id} is not in the game."}
#
#     current_state = games[game_id].next(message)
#     return {"message": current_state.status,
#             "error": current_state.error,
#             "current_node_state": current_state.name}


if __name__ == '__main__':
    import argparse
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", default=5000, help="Port of the server.")
    args = parser.parse_args()

    server = pywsgi.WSGIServer(('', args.port), app, handler_class=WebSocketHandler)
    server.serve_forever()
