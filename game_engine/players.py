import asyncio

from game_engine.state import IncorrectResponse


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None

        self._responses = asyncio.Queue()

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

    async def push_response(self, response):
        """
        Receives a message from the client
        Args:
            response:

        Returns:

        """
        await self._responses.put(response)

    async def response(self, validators=None):
        response = await self._responses.get()
        for validator in validators:
            response = validator.validate(response)
            if validator.failed:
                # TODO: send message to player
                raise IncorrectResponse(validator.get_message())
        return response


