import asyncio

import aiohttp

from game_engine.server import make_app, initialize_start_game


async def test_create_and_join_round(aiohttp_client, loop):
    app = make_app()
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

    async with client.ws_connect(f"/round/{response_data['id']}/join?playerId={response_data['playerId']}") as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                assert msg.json()['type'] == 'PLAYER_CONNECTED'
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
        await ws.send_json({"type": "PING"})
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                assert msg.json()['type'] == 'PONG'
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


async def send_receive_chat(client, round_id, player_id, username):
    received_messages = []
    async with client.ws_connect(f"/round/{round_id}/join?playerId={player_id}") as ws:
        print(f"{player_id} connected")
        await ws.send_json({
            'type': 'CHAT',
            'message': f"Hello! I'm {username}"
        })
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                msg_json = msg.json()
                if type(msg_json) == dict and 'type' in msg_json:
                    assert msg_json['type'] != "ERROR"

                    if msg_json['type'] == 'CLOSE':
                        print("closed")
                        break
                    elif msg_json['type'] == 'CHAT':
                        print(msg_json['author'], "says", msg_json['message'])
                        received_messages.append(msg_json)
                        assert msg_json['message'] == f"Hello! I'm {msg_json['author']}"

                        if len(received_messages) == 2:
                            break
                    else:
                        print(f"=== Player {player_id} received ===")
                        print(msg.json())
                else:
                    print(f"=== Player {player_id} received ===")
                    print(msg.json())
                    break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"Error for player {player_id}: {msg.exception()}")
                break


async def test_chat_feature(aiohttp_client, loop):
    app = make_app()
    usernames = ['player 1', 'player 2']
    round_id, clients, responses = await initialize_start_game(app, aiohttp_client, 'bataille', usernames)

    await asyncio.gather(*[send_receive_chat(clients[username],
                                             round_id,
                                             responses[username]['playerId'],
                                             username)
                           for username in usernames])


async def test_list_rounds(aiohttp_client, loop):
    app = make_app()
    usernames = ["player1", "player2"]
    game_id = "bataille"
    await initialize_start_game(app, aiohttp_client, game_id, usernames, {'public': True})
    client = await aiohttp_client(app)
    response = await client.get("/round/list")
    response_data = await response.json()
    assert type(response_data) == list
    assert len(response_data) == 1
    assert response_data[0]['gameId'] == game_id
    assert response_data[0]['players'] == usernames


async def test_list_games(aiohttp_client, loop):
    app = make_app()
    client = await aiohttp_client(app)
    response = await client.get("/game/list")
    response_data = await response.json()
    assert type(response_data) == list
    assert len(response_data)
    for game in response_data:
        assert 'gameId' in game
        assert 'description' in game
        assert 'rules' in game
        assert 'min_players' in game
        assert 'max_players' in game


async def test_game_info(aiohttp_client, loop):
    app = make_app()
    client = await aiohttp_client(app)
    response = await client.get("/game/list")
    available_games = await response.json()
    response = await client.get(f"/game/{available_games[0]['gameId']}")
    game = await response.json()
    for key, value in available_games[0].items():
        assert key in game
        assert game[key] == value
