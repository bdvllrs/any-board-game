import uuid

from aiohttp import web

from game_engine.players import Player


def generate_username():
    # TODO: funnier user names
    return uuid.uuid4().hex[:15]


async def initialize_server(app, aiohttp_client, game_name, usernames, create_round_params=None):
    create_round_params = {} if create_round_params is None else create_round_params

    username_master = usernames[0]
    clients = dict()
    responses = dict()
    responses_data = dict()
    for username in usernames:
        clients[username] = await aiohttp_client(app)

    create_round_params.update(dict(username=username_master))
    responses[username_master] = await clients[username_master].post(f"/round/create/{game_name}",
                                                                     json=create_round_params)
    responses_data[username_master] = await responses[username_master].json()

    round_id = responses_data[username_master]['id']

    for username in usernames[1:]:
        # player 2 connects
        responses[username] = await clients[username].get(f"/round/{round_id}/join",
                                                          params=dict(username=username))

        responses_data[username] = await responses[username].json()

    return round_id, clients, responses_data


def add_player_to_round(request, round_id, username):
    if username is None:
        username = generate_username()
    if round_id not in request.app['games'].keys():
        return web.json_response({}, status=404)

    game = request.app['games'][round_id]

    if game.started:
        return web.json_response({"message": "Game has already started."}, status=403)
    if username in map(lambda u: u.username, game.players.values()):
        return web.json_response({"message": f"Username {username} already exists."}, status=403)
    player_id = uuid.uuid4().hex
    player = Player(username, player_id)
    is_added = game.add_player(player)
    if not is_added:
        return web.json_response({"message": f"You cannot enter the game."}, status=403)
    return web.json_response({"playerId": player_id,
                              "id": round_id,
                              "gameId": game.game_id,
                              "status": "pending",
                              "createdOn": str(game.created_on),
                              "createdBy": game.created_by,
                              "minPlayers": game.min_players,
                              "maxPlayers": game.max_players,
                              "public": game.is_public,
                              "players": list(map(lambda u: u.username, game.players.values()))})