from game_engine.players import Player
from game_engine.games.bataille.main import BatailleGame


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

