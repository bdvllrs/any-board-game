class PlayerManager:
    def __init__(self, min_players=2, max_players=None):
        self.min_players = min_players
        self.max_players = max_players


class Player:
    def __init__(self, username, uid, socket_id):
        self.username = username
        self.uid = uid
        self.socket_id = socket_id
