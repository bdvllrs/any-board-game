from pathlib import Path
from runpy import run_path

import yaml


class GameEnvironment:
    def __init__(self,
                 players,
                 card_decks=None):
        self.players = players
        self.card_decks = card_decks

    def main_loop(self):
        pass


class GamePhase:
    pass
