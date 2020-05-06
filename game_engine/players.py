import asyncio


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None
        self.current_interface = None

        self._responses = asyncio.Queue()

        self.interfaces = dict()
        self.default_interface = None

    def add_interface(self, interface, is_default=False):
        self.interfaces[interface.name] = interface
        if is_default:
            self.default_interface = interface.name
            self.current_interface = self.default_interface

    def set_env(self, env):
        self.env = env

    async def init_player(self):
        await self.switch_interface(self.interfaces[self.current_interface])

    @property
    def socket(self):
        return self._socket

    @property
    def connected(self):
        return self._socket is not None

    def disconnect(self):
        self._socket = None

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

    async def response(self, validators=None, interface=None, act_on=None):
        """
        Asks for a response from the client
        Args:
            validators: list of validators to use
            interface: if provided will switch the client on this interface. The interface is reset to the previous
              interface after the transaction.
            act_on: if provided, specifies to the client on what component he should act on.

        Returns: response
        """
        if interface is not None:
            await self.switch_interface(interface)
        else:
            await self.switch_interface(self.interfaces[self.current_interface])

        if act_on is not None:
            await self.send({
                'type': 'ACTION_AWAITED',
                'on': act_on
            })

        is_response_received = False
        while not is_response_received:
            response = await self._responses.get()
            failed = False
            messages = []
            for validator in validators:
                response = validator.validate(response)
                if validator.failed:
                    failed = True
                    messages.append(validator.get_message())
            if not failed:
                is_response_received = True
            else:
                await self.socket.send_json({"type": "ERROR",
                                             "messages": messages})
        if interface is not None:
            await self.switch_interface(self.interfaces[self.current_interface])
        return response['data']
