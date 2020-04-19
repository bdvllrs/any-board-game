import datetime

from .events import EventManager
from .state import FiniteStateMachine


class GameInstance:
    """
    Event lifecycle of the game:
        1) GAME_STARTS: self-explanatory
        2) NODE_SETUP: when a node has finished setting up
        3) CLIENT_ACTED: the client has done an action. Callback params: player: Player, response: dict.
        4) NODE_EXECUTION_FAILED: the execution of the node failed
    """

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

        self.event_manager = EventManager()

        self.state_machine = FiniteStateMachine(self)

    def add_player(self, player):
        if self.can_add_player(player):
            player.env = self
            self.players[player.uid] = player
            return True
        return False

    def can_add_player(self, player):
        return len(self.players) < self.max_players

    def start(self):
        self.started = True

        self.event_manager.register("GAME_START", self.state_machine.step_setup)
        self.event_manager.trigger("GAME_START")
