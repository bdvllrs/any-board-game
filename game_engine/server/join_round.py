import asyncio

import aiohttp
from aiohttp import web

from game_engine.server.utils import add_player_to_round


async def join_game_route(request):
    """
    Route between the HTTP GET and the websocket.
    """
    # FIXME: better solution
    if 'username' in request.query:
        print(f'Received join request with username: creating user. {request.query}')
        return await join_game(request)
    else:
        print(f"Received socket request with {request.query}")
        return await join_round_socket(request)


async def join_round_socket(request):
    ws = web.WebSocketResponse()
    print(f'Created the websocket object: {ws}')
    await ws.prepare(request)
    print(f'Prepared the websocket connection: {ws}')

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
    await player.connect(ws)

    connected_players = filter(lambda p: p.connected, game.players.values())
    await asyncio.gather(*[p.socket.send_json({"type": "PLAYER_CONNECTED",
                                               "username": player.username,
                                               "message": f"Say hello to {player.username}."})
                           for p in connected_players])

    # Listen for messages
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'CLOSE':
                player.disconnect()
                await asyncio.gather(*[p.socket.send_json({"type": "PLAYER_DISCONNECTED", "username": player.username})
                                       for p in game.players.values() if p.connected])
                await ws.close()
            else:
                json_msg = msg.json()
                if type(json_msg) == dict and "type" in json_msg:
                    print("Server received", json_msg)
                    if json_msg['type'] == 'PING':
                        await ws.send_json({"type": "PONG"})
                    # Start the game
                    elif json_msg['type'] == "START_GAME" and game.created_by == player.username and not game.started:
                        await asyncio.gather(*[p.send({"type": "GAME_STARTED"})
                                               for p in game.players.values()])
                        asyncio.create_task(game.start())
                    elif json_msg['type'] == "CHAT":
                        await asyncio.gather(*[p.send({"type": "CHAT",
                                                       "message": json_msg['message'],
                                                       "author": player.username})
                                               for p in game.players.values()])
                    else:
                        await player.push_response(json_msg)
                # await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
            player.disconnect()
            await asyncio.gather(*[p.send({"type": "PLAYER_DISCONNECTED", "username": player.username})
                                   for p in game.players.values()])

    return ws


async def join_game(request):
    username = request.query['username'] if 'username' in request.query else None
    round_id = request.match_info['round_id']
    return add_player_to_round(request, round_id, username)