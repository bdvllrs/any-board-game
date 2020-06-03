import asyncio

import aiohttp
import numpy as np
from pathlib import Path

from .game import BatailleGame
from game_engine.players import Player
from game_engine.server import make_app, initialize_start_game


game_folder = Path(__file__).parents[1].resolve()


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


def choose_card_to_play(hand, played_cards, cards):
    # If has one spade, plays it
    for card_id in hand:
        card = cards[card_id]
        if card['state']['suit'] == 'S':
            return card_id
    # Or look for card that doesn't make you lose
    for card_id in hand:
        card = cards[card_id]
        for played_card_id in played_cards:
            played_card = cards[played_card_id]
            if int(card['state']['value']) > int(played_card['state']['value']):
                return card_id
    # Or random card
    return hand[0]


async def bataille_player(client, round_id, player_id, is_master=False):
    async with client.ws_connect(f"/round/{round_id}/join?playerId={player_id}") as ws:
        print(f"{player_id} connected")
        connected_players = []
        player_hand = []
        played_cards = []
        cards = {}

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
                    elif msg_json['type'] == 'COMPONENTS_UPDATES':
                        print(f"=CLIENT {player_id}=  COMPONENTS_UPDATES")
                        print(msg_json)
                        assert 'components' in msg_json
                        for component in msg_json['components']:
                            if component['type'] in ['Create', 'Update']:
                                assert 'id' in component
                                assert 'component' in component
                                assert 'type' in component['component']
                                if component['id'] == 'played_cards':
                                    played_cards = component['component']['cards']
                                elif component['id'] == 'hand':
                                    player_hand = component['component']['cards']
                                elif component['component']['type'] == 'Card':
                                    cards[component['id']] = component['component']
                            elif component['type'] == "Delete":
                                # TODO
                                pass
                    elif msg_json['type'] == 'INTERFACE_UPDATE':
                        print(f"=CLIENT {player_id}=  INTERFACE_UPDATE")
                        print(msg_json)
                        assert 'components' in msg_json
                    elif msg_json['type'] == 'ACTION_AWAITED':
                        print(f"=CLIENT {player_id}=  ACTION_AWAITED")
                        print(msg_json)
                        assert 'all_of' in msg_json
                        assert type(msg_json['all_of']) == list
                        assert len(msg_json['all_of']) == 1
                        action = msg_json['all_of'][0]
                        assert 'type' in action
                        assert 'target_component' in action
                        assert action['type'] == "OnClick"
                        assert action['target_component'] == 'hand'

                        picked_card = choose_card_to_play(player_hand, played_cards, cards)

                        await ws.send_json({
                            "type": "ACTION_RESPONSE",
                            "hand": picked_card
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
    app = make_app(game_folder)

    game_name = "bataille"
    usernames = ["test1", "test2", "test3"]
    round_id, clients, response_data = await initialize_start_game(app, aiohttp_client, game_name, usernames)

    await asyncio.gather(*[bataille_player(clients[username],
                                           round_id,
                                           response_data[username]['playerId'],
                                           username == usernames[0])
                           for username in usernames])
