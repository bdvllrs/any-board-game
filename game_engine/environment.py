from pathlib import Path
from runpy import run_path

import yaml


class GameEnvironment:
    def __init__(self, folder, players):
        self.folder = folder if isinstance(folder, Path) else Path(folder)
        self.players = players

        if not (self.folder / "game.yaml").exists():
            raise ValueError(f"game.yaml does not exist for the game {folder}.")
        if not (self.folder / "actions.py").exists():
            raise ValueError(f"actions.py does not exist for the game {folder}.")

        with open(self.folder / "game.yaml", "r") as game_conf_file:
            self.game_conf = yaml.load(game_conf_file, Loader=yaml.SafeLoader)

        # Load action.py file
        self.actions = run_path(str(self.folder / "actions.py"))

        # Possible status: GAME_FINISHED
        self.status = []

        if (len(self.players) < self.game_conf['num_players']['min'] or
                len(self.players) > self.game_conf['num_players']['max']):
            raise ValueError("The number of player is incorrect.")

    def parse_game_step(self, step, **context):
        assert type(step) == dict
        if 'turns' in step.keys():
            self.parse_game_turn(step['turns'])
        elif 'actions' in step.keys():
            for action in step['actions']:
                self.perform_action(action, **context)

    def parse_game_turn(self, turn):
        if 'setup_turn' in turn.keys():
            # Turn setup
            self.parse_game_step(turn['setup_turn'])
        if 'actions' in turn.keys():
            for player in self.players:
                self.parse_game_step(turn['actions'],
                                     player=player)
        if 'resolve_turn' in turn.keys():
            # resolve turn
            self.parse_game_step(turn['resolve_turn'])

    def perform_action(self, action, player=None):
        print(action)
        print("oui")

    def main_loop(self):
        while "GAME_FINISHED" not in self.status:
            for step in self.game_conf['game']:
                self.parse_game_step(step)
