

class GameInstance:
    def __init__(self, game_id):
        self._game_id = game_id
        self._players = dict()
        self.started = False

    def get_state(self):
        raise NotImplementedError

    def add_player(self, player):
        self._players[player.uid] = player

    def start(self):
        self.started = True

    def next(self):
        pass

    def get_players(self, uids=None):
        if uids is not None:
            return [player for uid, player in self._players.items() if uid in uids]
        return self._players.values()
