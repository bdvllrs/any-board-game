import aiohttp

from game_engine.server import make_app


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
