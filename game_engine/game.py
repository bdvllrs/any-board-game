from .state import FiniteStateMachine


class GameInstance:
    def __init__(self, game_id):
        self.game_id = game_id
        self.players = dict()
        self.started = False

        self.state_machine = FiniteStateMachine(self)

    def add_player(self, player):
        if self.can_add_player(player):
            self.players[player.uid] = player
            return True
        return False

    def can_add_player(self, player):
        return True

    def start(self):
        self.started = True
