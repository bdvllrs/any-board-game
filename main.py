from game_engine.environment import GameEnvironment
from game_engine.players import Player
import deepcopy

if __name__ == '__main__':
    players = [
        Player("Ben"),
        Player("Ben 2"),
    ]
    env = GameEnvironment("games/citadel/few_players",
                          players)

    env.main_loop()

def foo(state):
    state = deepcopy.deepcopy(state)
    state.bar = 123
    return state
