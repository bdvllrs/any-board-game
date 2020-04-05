from game_engine.state import Triggers


class GameInstance:
    def __init__(self, game_id):
        self._game_id = game_id
        self._players = dict()
        self.started = False
        self.state_generator = None

    def get_state(self):
        raise NotImplementedError

    def add_player(self, player):
        self._players[player.uid] = player

    def start(self):
        self.started = True
        self.state_generator = self.get_state().execute()

    def next(self, message=None):
        if message is not None:
            self.get_state().client_messages.append(message)

        new_state = next(self.state_generator)

        return new_state

    def get_players(self, uids=None):
        if uids is not None:
            return [player for uid, player in self._players.items() if uid in uids]
        return self._players.values()
