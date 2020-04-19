class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None

    @property
    def socket(self):
        return self._socket

    @socket.setter
    def socket(self, socket):
        if self._socket is not None:
            self._socket.close()
        self._socket = socket

    def send(self, message, callback=None, err_callback=None, condition=None):
        """
        Sends a message to the client
        Args:
            message: message to send
            callback: a callback function to handle the response
            err_callback: an error callback to handle the case of failing callback
            condition: an added condition for the event manager
        """
        self._socket.send(message)
        if callback is not None:
            self.env.event_mananager.register("CLIENT_ACTED", callback, err_callback, condition)

    def receive(self, response):
        """
        Receives a message from the client
        Args:
            response:

        Returns:

        """
        self.env.event_mananager.trigger("CLIENT_ACTED", self, response)
