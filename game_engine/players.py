class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid

        self._to_client_messages = []
        self._from_client_messages = []

    def send(self, message, callback=None):
        """
        Sends a message to the interface of the player.
        Args:
            message: content of the message
            callback: function called when a response is received. The callback will be given as argument the response.
        """
        self._to_client_messages.append(dict(content=message, callback=callback))

    def get_message(self, from_="server"):
        message_list = self._to_client_messages if from_ == "server" else self._from_client_messages
        if len(message_list):
            return message_list.pop(0)
        return None

    def receive(self, response, callback=None):
        self._from_client_messages.append(dict(content=response, callback=callback))
