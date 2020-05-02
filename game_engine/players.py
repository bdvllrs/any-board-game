import asyncio

from game_engine.state import IncorrectResponse


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None
        self.current_interface = None

        self._responses = asyncio.Queue()

    def set_env(self, env):
        self.env = env
        self.current_interface = env.default_interface

    async def init_player(self):
        await self.switch_interface(self.env.interfaces[self.current_interface])

    @property
    def socket(self):
        return self._socket

    async def set_socket(self, socket):
        if self._socket is not None:
            await self._socket.close()
        self._socket = socket

    async def switch_interface(self, interface):
        await self.send({
            "type": "INTERFACE_UPDATE",
            **interface.get_client_update()
        })
        self.current_interface = interface.name

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

    async def response(self, validators=None, interface=None):
        """
        Asks for a response from the client
        Args:
            validators: list of validators to use
            interface: if provided will switch the client on this interface. The interface is reset to the previous interface
              after the transaction.

        Returns: response
        """
        if interface is not None:
            await self.switch_interface(interface)
        response = await self._responses.get()
        for validator in validators:
            response = validator.validate(response)
            if validator.failed:
                # TODO: send message to player
                raise IncorrectResponse(validator.get_message())
        if interface is not None:
            await self.switch_interface(self.env.interfaces[self.current_interface])
        return response
