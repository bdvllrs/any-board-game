class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid

        self._messages = []
        self._responses = []

    def send(self, message, callback=None):
        """
        Sends a message to the interface of the player.
        Args:
            message: content of the message
            callback: function called when a response is received. The callback will be given as argument the response.
        """
        self._messages.append(dict(content=message, callback=callback))

    def get_message(self):
        if len(self._messages):
            return self._messages.pop(0)
        return None

    def receive(self, response, callback=None):
        self._responses.append(dict(content=response, callback=callback))
