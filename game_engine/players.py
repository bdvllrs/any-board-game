import asyncio
from copy import deepcopy


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None
        self.current_interface = None

        self._responses = asyncio.Queue()

        self._waiting_messages = []

        self.interface_selector_fn = None

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

    async def update_interface(self, node):
        if self.interface_selector_fn is not None:
            self.current_interface = self.interface_selector_fn(node, self)
        await self.switch_interface(self.interfaces[self.current_interface])

    @property
    def socket(self):
        return self._socket

    @property
    def connected(self):
        return self._socket is not None and not self._socket.closed

    def disconnect(self):
        self._socket = None

    async def connect(self, socket):
        if self._socket is not None:
            await self._socket.close()
        self._socket = socket

        # Send pending messages
        waiting_messages = deepcopy(self._waiting_messages)  # insures that no infinite loop if re deconnects.
        self._waiting_messages = []
        for message in waiting_messages:
            await self.send(message)

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
        if self.connected:
            await self._socket.send_json(message)
        else:  # Don't block everyone
            self._waiting_messages.append(message)

    async def push_response(self, response):
        """
        Receives a message from the client
        Args:
            response:

        Returns:

        """
        await self._responses.put(response)

    async def response(self, validators=None, act_on=None):
        """
        Asks for a response from the client
        Args:
            validators: list of validators to use
            act_on: if provided, specifies to the client on what component he should act on.

        Returns: response
        """
        if act_on is not None:
            await self.send({
                'type': 'ACTION_AWAITED',
                'on': act_on
            })

        is_correct_response = False
        while not is_correct_response:
            response = await self._responses.get()
            failed = False
            messages = []
            for validator in validators:
                response = validator.validate(response)
                if validator.failed:
                    failed = True
                    messages.append(validator.get_message())
            if not failed:
                is_correct_response = True
            else:
                await self.socket.send_json({"type": "ERROR",
                                             "messages": messages})
        return response['data']
