from game_engine.events import Event
from game_engine.state import IncorrectResponse


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None

        self._responses = []
        self._response_event = Event()

    @property
    def socket(self):
        return self._socket

    @socket.setter
    def socket(self, socket):
        if self._socket is not None:
            self._socket.close()
        self._socket = socket

    async def send(self, message):
        """
        Sends a message to the client
        Args:
            message: message to send
        """
        await self._socket.send_json(message)

    def push_response(self, response):
        """
        Receives a message from the client
        Args:
            response:

        Returns:

        """
        self._responses.append(response)
        self._response_event.trigger()

    async def response(self, validators=None):
        await self._response_event.wait()
        for validator in validators:
            if not validator.validate():
                # TODO: send message to player
                raise IncorrectResponse(validator.get_message())
        return self._responses.pop(0)


