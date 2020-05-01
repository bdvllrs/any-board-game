import datetime

from .state import FiniteStateMachine


class GameEnv:
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

        self.state_history = [dict()]

        self.state_machine = FiniteStateMachine(self)

        self.interfaces = dict()
        self.current_interface = None

    def add_interface(self, interface, is_default=False):
        self.interfaces[interface.name] = interface
        if is_default:
            self.current_interface = interface.name

    @property
    def state(self):
        return self.state_history[-1]

    def step_state(self):
        self.state_history.append(self.state.copy())

    def revert_state(self):
        self.state_history.pop()
        if not len(self.state_history):
            self.state_history = [dict()]

    def add_player(self, player):
        if self.can_add_player(player):
            player.env = self
            self.players[player.uid] = player
            return True
        return False

    async def setup(self):
        pass

    def can_add_player(self, player):
        return len(self.players) < self.max_players

    async def start(self):
        self.started = True

        await self.setup()

        async for node in self.state_machine:
            pass
