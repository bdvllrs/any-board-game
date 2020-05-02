import asyncio

import aiohttp

from game_engine.games.bataille.main import BatailleGame
from game_engine.players import Player
from game_engine.server import app


async def test_bataille_game_setup():
    num_players = 2
    game_instance = BatailleGame("0", "player0", False)
    players = [Player(f"player{idx}", str(idx)) for idx in range(num_players)]
    for player in players:
        game_instance.add_player(player)

    assert len(game_instance.players) == len(players)

    game_instance.started = True
    await game_instance.setup()

    assert 'hands' in game_instance.state
    assert len(game_instance.state['hands']) == len(game_instance.players)


async def bataille_player(client, round_id, player_id):
    async with client.ws_connect(f"/round/{round_id}/join?playerId={player_id}") as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.json()['type'] == 'CLOSE':
                    break
                else:
                    print(f"=== Player {player_id} received ===")
                    print(msg.json())
                    break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"Error for player {player_id}: {msg.exception()}")
                break


async def test_bataille_game(aiohttp_client, loop):
    client = await aiohttp_client(app)
    game_name = "bataille"
    usernames = ["test1", "test2", "test3"]
    response = await client.post(f"/round/create/{game_name}",
                                 json=dict(username=usernames[0]))
    response_data = await response.json()
    assert response_data['createdBy'] == usernames[0]
    assert response_data['id'] in client.app['games']

    # player 2 connects
    response_player2 = await client.get(f"/round/{response_data['id']}/join",
                                        params=dict(username=usernames[1]))

    response_data_player2 = await response_player2.json()
    assert response_data_player2['gameId'] == response_data['gameId']

    # player 3 connects
    response_player3 = await client.get(f"/round/{response_data['id']}/join",
                                        params=dict(username=usernames[2]))

    response_data_player3 = await response_player3.json()
    assert response_data_player3['gameId'] == response_data['gameId']

    asyncio.create_task(bataille_player(client, response_data['id'], response_data['playerId']))
    asyncio.create_task(bataille_player(client, response_data_player2['id'], response_data_player2['playerId']))
    asyncio.create_task(bataille_player(client, response_data_player3['id'], response_data_player3['playerId']))
