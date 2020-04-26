import asyncio
import traceback
import uuid

import aiohttp
from aiohttp import web

from game_engine.games.bataille.main import BatailleGame
from game_engine.players import Player

routes = web.RouteTableDef()


def generate_username():
    # TODO: funnier user names
    return uuid.uuid4().hex[:15]


@routes.get("/round/{round_id}/join")
async def join_game_route(request):
    """
    Route between the HTTP GET and the websocket.
    """
    # FIXME: better solution
    if 'username' in request.query:
        return await join_game(request)
    else:
        return await join_round_socket(request)


async def join_round_socket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    round_id = request.match_info['round_id']

    query = request.query

    # Check that the query and given information is correct
    if 'playerId' not in query:
        await ws.send_json({"status": 403, "message": "PlayerId is required."})
        await ws.close()
        return ws

    player_id = query['playerId']

    if round_id not in request.app['games'].keys():
        await ws.send_json({"status": 403, "message": "RoundId is incorrect."})
        await ws.close()
        return ws

    game = request.app['games'][round_id]

    if player_id not in game.players:
        await ws.send_json({"status": 403, "message": "Player has not joined the game."})
        await ws.close()
        return ws

    player = game.players[player_id]
    player.socket = ws

    # Listen for messages
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'CLOSE':
                await ws.close()
            else:
                json_msg = msg.json()
                if "type" in json_msg:
                    if json_msg['type'] == 'PING':
                        await ws.send_json({"type": "PONG"})
                        await ws.send_json({"type": "CLOSE"})
                    # Start the game
                    elif json_msg['type'] == "START_GAME" and game.created_by == player.username and not game.started:
                        asyncio.create_task(game.start())
                        await asyncio.gather(*[player.socket.send_json({"type": "GAME_STARTED"})
                                               for player in game.players])
                    else:
                        await player.push_response(json_msg)
                # await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    return ws


async def join_game(request):
    username = request.query['username'] if 'username' in request.query else None
    round_id = request.match_info['round_id']
    return add_player_to_round(request, round_id, username)


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


@routes.post('/round/create/{game_id}')
async def start_game(request):
    form = await request.json()
    form = dict(form)
    game_id = request.match_info['game_id']
    if 'username' not in form:
        form['username'] = generate_username()
    if 'public' not in form:
        form['public'] = False
    creator_username = form['username']
    is_game_public = form['public']  # TODO: public game is_game_public = False
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
    return add_player_to_round(request, round_id, creator_username)


app = web.Application()

app['games'] = dict()

app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app)
