import uuid
import logging

from aiohttp import web

from any_board_game.server.join_round import join_game_route
from any_board_game.server.utils import generate_username, add_player_to_round, get_game_from_game_id, get_available_games


async def start_game(request):
    logging.info(f"Request: {request.url}")

    form = await request.json()
    form = dict(form)
    game_id = request.match_info['game_id']
    if 'username' not in form:
        form['username'] = generate_username()
    if 'public' not in form:
        form['public'] = False
    creator_username = form['username']
    is_game_public = form['public']
    round_id = uuid.uuid4().hex
    game_conf = get_game_from_game_id(game_id)
    logging.debug("Game conf")
    logging.debug(game_conf)
    if game_conf is not None:
        game_class = game_conf['game_env']['__class']
        try:
            request.app['games'][round_id] = game_class(round_id, creator_username, is_game_public)
        except Exception as e:
            # traceback.print_tb(e.__traceback__)
            logging.exception(e)
            return web.json_response({"message": f"An unexpected error has occurred. \n {e}"}, status=500)
    else:
        logging.error(f"Game {game_id} does not exsis.")
        return web.json_response({"message": "Game does not exists."}, status=404)

    response = add_player_to_round(request, round_id, creator_username)
    logging.info(f'Creating game: {response}')
    return response


async def list_rounds(request):
    logging.info(f"Request: {request.url}")
    games = []
    for round_id, game in request.app['games'].items():
        if game.is_public:
            games.append({
                'gameId': game.game_id,
                'roundId': round_id,
                'started': game.started,
                'players': [player.username for player in game.players.values()],
                'createdOn': str(game.created_on),
                'createdBy': game.created_by
            })
    return web.json_response(games)


async def list_games(request):
    logging.info(f"Request: {request.url}")
    available_games = get_available_games()
    games = []
    for game in available_games:
        games.append({
            'gameId': game['game_env']['__class'].game_id,
            'rules': game['rules'],
            'description': game['description'],
            'min_players': game['game_env']['__class'].min_players,
            'max_players': game['game_env']['__class'].max_players
        })
    return web.json_response(games)


async def game_info(request):
    logging.info(f"Request: {request.url}")
    game_id = request.match_info['game_id']
    game = get_game_from_game_id(game_id)
    if game is not None:
        infos = {
            'gameId': game['game_env']['__class'].game_id,
            'rules': game['rules'],
            'description': game['description'],
            'min_players': game['game_env']['__class'].min_players,
            'max_players': game['game_env']['__class'].max_players
        }
        return web.json_response(infos)
    return web.json_response({"message": "Game does not exists."}, status=404)


def make_app():
    app = web.Application()
    app['games'] = dict()

    app.add_routes([
        web.get("/round/{round_id}/join", join_game_route),
        web.post('/round/create/{game_id}', start_game),
        web.get('/round/list', list_rounds),
        web.get('/game/list', list_games),
        web.get('/game/{game_id}', game_info),
    ])

    return app


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="AnyBoardGame")
    parser.add_argument('--port', '-p', type=int, default=42802,
                        help='Port of the application.')
    args = parser.parse_args()

    app = make_app()
    web.run_app(app, port=args.port)
