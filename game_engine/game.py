import datetime

from .state import FiniteStateMachine


class GameInstance:
    min_players = 2
    max_players = 100
    game_id = "untitled"

    def __init__(self, game_id, created_by, is_public):
        self.game_id = game_id
        self.players = dict()
        self.started = False
        self.created_on = datetime.datetime.now()
        self.created_by = created_by
        self.is_public = is_public

        self.state = dict()

        self.state_machine = FiniteStateMachine(self)

    def add_player(self, player):
        if self.can_add_player(player):
            self.players[player.uid] = player
            return True
        return False

    def can_add_player(self, player):
        return len(self.players) < self.max_players

    def start(self):
        self.started = True

    def step(self):
        raise NotImplementedError
