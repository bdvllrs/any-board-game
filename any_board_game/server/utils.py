import importlib.util
import logging
import os
import uuid

import yaml
from aiohttp import web

from any_board_game.players import Player
from any_board_game.utils import games_folder


def generate_username():
    """
    Generates username for player without one
    """
    # TODO: funnier user names
    return uuid.uuid4().hex[:15]


async def initialize_start_game(app, aiohttp_client, game_name, usernames, create_round_params=None):
    """
    Utils for tests. Initialize a game
    Args:
        app:
        aiohttp_client:
        game_name:
        usernames:
        create_round_params:

    Returns:

    """
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
        logging.error("Player cannot enter an already started game.")
        return web.json_response({"message": "Game has already started."}, status=403)
    if username in map(lambda u: u.username, game.players.values()):
        logging.error(f"{username} is already taken. Choose another one.")
        return web.json_response({"message": f"Username {username} is already taken."}, status=403)
    player_id = uuid.uuid4().hex
    player = Player(username, player_id)
    is_added = game.add_player(player)
    if not is_added:
        logging.error("Player cannot enter this game."
                      "Because there are already to many player or does't fit the GameEnv.can_add_player condition.")
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


def make_game_config(config) -> dict:
    default_config = {
        "rule_book": None,
        "description": "No description.",
        "rules": "No rules added."
    }
    default_config.update(config)
    if default_config['rule_book'] is not None:
        with open(os.path.join(default_config['__game_location'], default_config['rule_book']), 'r') as rule_file:
            default_config['rules'] = rule_file.read()
    return default_config


def get_available_games():
    """
    Loads and returns games in the games folder.
    """
    games = []
    logging.debug(f"Loading games from {str(games_folder)}")
    for folder in games_folder.iterdir():
        if folder.is_dir():
            for file in folder.iterdir():
                if file.name == 'config.yaml':
                    with open(file, 'r') as config_file:
                        yaml_config = yaml.safe_load(config_file)
                    if ('game_env' in yaml_config and 'location' in yaml_config['game_env']
                            and 'name' in yaml_config['game_env']):
                        yaml_config['__game_location'] = file.resolve().parent
                        game_env_location = str(file.resolve().parent / yaml_config['game_env']['location'])
                        spec = importlib.util.spec_from_file_location("game_env", game_env_location)
                        game_env = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(game_env)
                        yaml_config['game_env']['__class'] = getattr(game_env, yaml_config['game_env']['name'])

                        logging.debug(f"Found game {yaml_config['game_env']['__class'].game_id}")

                        games.append(make_game_config(yaml_config))
    return games


def get_game_from_game_id(game_id):
    """
    Gets the game infos of a specific requested game_id
    Args:
        game_id:

    Returns: Game config or None.
    """
    games = get_available_games()
    for game in games:
        if game['game_env']['__class'].game_id == game_id:
            return game
