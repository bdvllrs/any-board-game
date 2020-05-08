import asyncio
import datetime
from copy import deepcopy

from .state import FiniteStateMachine


class GameEnv:
    min_players = 2
    max_players = 100
    game_id = "untitled"

    def __init__(self, round_id, created_by, is_public):
        self.round_id = round_id
        self.players = dict()
        self.started = False
        self.created_on = datetime.datetime.now()
        self.created_by = created_by
        self.is_public = is_public

        self.winner_players = []

        self.state_history = [dict()]

        self.state_machine = FiniteStateMachine(self)

    @property
    def state(self):
        return self.state_history[-1]

    def add_winner(self, player):
        self.winner_players.append(player.username)

    def step_state(self):
        copied_state = deepcopy(self.state)
        self.state_history.append(copied_state)

    def revert_state(self):
        self.state_history.pop()
        if not len(self.state_history):
            self.state_history = [dict()]

    def add_player(self, player):
        if self.can_add_player(player):
            player.set_env(self)
            self.players[player.uid] = player
            return True
        return False

    async def setup(self):
        pass

    def can_add_player(self, player):
        return len(self.players) < self.max_players

    def bind_interface(self, node, player):
        return player.interfaces[player.current_interface]

    async def start(self):
        self.started = True

        await self.setup()

        async for node in self.state_machine:
            await asyncio.gather(*[player.update_interface(self.state_machine.nodes[node])
                                   for player in self.players.values()])

        await asyncio.gather(*[player.send({
            "type": "GAME_FINISHED",
            "winners": self.winner_players
        }) for player in self.players.values()])
