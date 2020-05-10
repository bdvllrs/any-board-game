import asyncio

import aiohttp
import numpy as np

from game_engine.games.bataille.game import BatailleGame
from game_engine.players import Player
from game_engine.server import make_app, initialize_start_game
from game_engine.utils import games_folder


async def test_bataille_game_setup():
    assert len(list(games_folder)) == 6
    assert str(games_folder) == "/home/runner/work/GameEngine/GameEngine/game_engine/games"
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


def choose_card_to_play(hand, played_cards):
    # If has one spade, plays it
    for card in hand:
        if card['suit'] == 'S':
            return card
    # Or look for card that doesn't make you lose
    for card in hand:
        for played_card in played_cards:
            if card['value'] > played_card['value']:
                return card
    # Or random card
    return hand[0]


async def bataille_player(client, round_id, player_id, is_master=False):
    async with client.ws_connect(f"/round/{round_id}/join?playerId={player_id}") as ws:
        print(f"{player_id} connected")
        connected_players = []
        player_hand = []
        played_cards = []
        winners = None

        num_steps = 0

        async for msg in ws:
            num_steps += 1
            if num_steps >= 100:
                break
            if msg.type == aiohttp.WSMsgType.TEXT:
                msg_json = msg.json()
                if type(msg_json) == dict and 'type' in msg_json:
                    assert msg_json['type'] != "ERROR"

                    if msg_json['type'] == 'CLOSE':
                        print(f"=CLIENT {player_id}=  CLOSE")
                        break
                    elif msg_json['type'] == 'PLAYER_CONNECTED':
                        print(f"=CLIENT {player_id}=  PLAYER_CONNECTED")
                        print(msg_json)
                        connected_players.append(msg_json)
                        if is_master and len(connected_players) == 3:
                            await ws.send_json({"type": "START_GAME"})
                    elif msg_json['type'] == 'INTERFACE_UPDATE':
                        print(f"=CLIENT {player_id}=  INTERFACE_UPDATE")
                        print(msg_json)
                        assert 'components' in msg_json
                        assert 'played_cards' in msg_json['components']
                        assert 'hand' in msg_json['components']
                        played_cards = msg_json['components']['played_cards']['cards']
                        player_hand = msg_json['components']['hand']['cards']
                    elif msg_json['type'] == 'ACTION_AWAITED':
                        print(f"=CLIENT {player_id}=  ACTION_AWAITED")
                        print(msg_json)
                        assert 'on' in msg_json
                        assert msg_json['on'] == ['hand']

                        picked_card = choose_card_to_play(player_hand, played_cards)

                        await ws.send_json({
                            "type": "ACTION_RESPONSE",
                            "data": picked_card
                        })
                    elif msg_json['type'] == 'GAME_FINISHED':
                        print(f"=CLIENT {player_id}=  GAME_FINISHED")
                        print(msg_json)
                        assert 'winners' in msg_json
                        winners = msg_json['winners']
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

        assert winners is not None


async def test_bataille_game(aiohttp_client, loop):
    np.random.seed(0)
    app = make_app()

    game_name = "bataille"
    usernames = ["test1", "test2", "test3"]
    round_id, clients, response_data = await initialize_start_game(app, aiohttp_client, game_name, usernames)

    await asyncio.gather(*[bataille_player(clients[username],
                                           round_id,
                                           response_data[username]['playerId'],
                                           username == usernames[0])
                           for username in usernames])
