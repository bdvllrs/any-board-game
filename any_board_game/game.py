import asyncio
import datetime
import logging
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

        self.state = dict()

        self.state_machine = FiniteStateMachine(self)

    def add_winner(self, player):
        self.winner_players.append(player.username)

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
        if player.current_interface is not None:
            return player.current_interface
        return player.default_interface

    async def start(self):
        self.started = True
        logging.info(f"Starting game {self.round_id}.")

        logging.info(f"Setting game {self.round_id} up.")
        await self.setup()

        async for node in self.state_machine:
            logging.info(f"Game {self.round_id} enters node {node}")

            await asyncio.gather(*[player.update_interface(self.state_machine.nodes[node])
                                   for player in self.players.values()])

        await asyncio.gather(*[player.send({
            "type": "GAME_FINISHED",
            "winners": self.winner_players
        }) for player in self.players.values()])
