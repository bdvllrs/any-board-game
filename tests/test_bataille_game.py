from game_engine.players import Player
from game_engine.games.bataille.main import BatailleGame


def test_bataille_game():
    game_instance = BatailleGame("0")
    player1 = Player("player 1", "0")
    player2 = Player("player 2", "1")
    game_instance.add_player(player1)
    game_instance.add_player(player2)

    game_instance.start()
