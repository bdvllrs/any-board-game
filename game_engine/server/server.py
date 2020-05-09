import traceback
import uuid

from aiohttp import web

from game_engine.games.bataille.game import BatailleGame
from game_engine.server.join_round import join_game_route
from game_engine.server.utils import generate_username, add_player_to_round


async def start_game(request):
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
    # TODO: automatically load all game in the folder
    if game_id == "bataille":
        try:
            request.app['games'][round_id] = BatailleGame(round_id, creator_username, is_game_public)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            print(e)
            return web.json_response({"message": f"An unexpected error has occurred. \n {e}"}, status=500)
    else:
        return web.json_response({"message": "Game does not exists."}, status=404)

    response = add_player_to_round(request, round_id, creator_username)
    print(f'Creating game: {response}')
    return response


async def list_rounds(request):
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


def make_app():
    app = web.Application()
    app['games'] = dict()

    app.add_routes([
        web.get("/round/{round_id}/join", join_game_route),
        web.post('/round/create/{game_id}', start_game),
        web.get('/round/list', list_rounds)
    ])

    return app


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="AnyBoardGame")
    parser.add_argument('--port', '-p', type=int, default=8080,
                        help='Port of the application.')
    args = parser.parse_args()

    app = make_app()
    web.run_app(app, port=args.port)