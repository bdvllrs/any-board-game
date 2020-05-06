import asyncio

import aiohttp

from game_engine.games.bataille.main import BatailleGame
from game_engine.players import Player
from game_engine.server import make_app


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


async def bataille_player(client, round_id, player_id, is_master=False):
    async with client.ws_connect(f"/round/{round_id}/join?playerId={player_id}") as ws:
        print(f"{player_id} connected")
        connected_players = []
        player_hand = []
        winners = None

        num_steps = 0

        async for msg in ws:
            if num_steps >= 10:
                break
            if msg.type == aiohttp.WSMsgType.TEXT:
                msg_json = msg.json()
                if type(msg_json) == dict and 'type' in msg_json:
                    assert msg_json['type'] != "ERROR"

                    if msg_json['type'] == 'CLOSE':
                        print("closed")
                        break
                    elif msg_json['type'] == 'PLAYER_CONNECTED':
                        connected_players.append(msg_json)
                        if is_master and len(connected_players) == 3:
                            await ws.send_json({"type": "START_GAME"})
                    elif msg_json['type'] == 'INTERFACE_UPDATE':
                        print("Interface Updated")
                        assert 'components' in msg_json
                        assert 'played_cards' in msg_json['components']
                        assert 'hand' in msg_json['components']
                        player_hand = msg_json['components']['hand']['cards']
                    elif msg_json['type'] == 'ACTION_AWAITED':
                        print("Do action")
                        assert 'on' in msg_json
                        assert msg_json['on'] == ['hand']
                        picked_card = player_hand[0]

                        await ws.send_json({
                            "type": "ACTION_RESPONSE",
                            "data": picked_card
                        })
                    elif msg_json['type'] == 'GAME_FINISHED':
                        print("Game finished")
                        assert 'winners' in msg_json
                        winners = msg_json['winners']
                        break
                    else:
                        print(f"=== Player {player_id} received ===")
                        print(msg.json())
                else:
                    print(f"=== Player {player_id} received ===")
                    print(msg.json())
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"Error for player {player_id}: {msg.exception()}")
                break

        assert winners is not None


async def test_bataille_game(aiohttp_client, loop):
    app = make_app()

    game_name = "bataille"
    usernames = ["test1", "test2", "test3"]
    username_master = usernames[0]
    clients = dict()
    responses = dict()
    responses_data = dict()
    for username in usernames:
        clients[username] = await aiohttp_client(app)

    responses[username_master] = await clients[username_master].post(f"/round/create/{game_name}",
                                                                     json=dict(username=username_master))
    responses_data[username_master] = await responses[username_master].json()

    round_id = responses_data[username_master]['id']

    for username in usernames[1:]:
        # player 2 connects
        responses[username] = await clients[username].get(f"/round/{round_id}/join",
                                                          params=dict(username=username))

        responses_data[username] = await responses[username].json()

    await asyncio.gather(*[bataille_player(clients[username],
                                           round_id,
                                           responses_data[username]['playerId'],
                                           username == username_master)
                           for username in usernames])
