import asyncio

import aiohttp

from game_engine.server import make_app


async def initialize_server(aiohttp_client, game_name, usernames):
    app = make_app()

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

    return round_id, clients, responses_data


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
    usernames = ['player 1', 'player 2']
    round_id, clients, responses = await initialize_server(aiohttp_client, 'bataille', usernames)

    await asyncio.gather(*[send_receive_chat(clients[username],
                                             round_id,
                                             responses[username]['playerId'],
                                             username)
                           for username in usernames])
