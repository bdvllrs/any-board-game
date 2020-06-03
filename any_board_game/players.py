import asyncio
import logging
from copy import deepcopy

from any_board_game.validators import ValidationException


def action_to_components(action_request, action_response, interface):
    response = {}
    for action in action_request['all_of']:
        if action['type'] == "OnClick":
            target_component = action['target_component']

            if target_component not in action_response.keys():
                raise ValueError()

            response[target_component] = interface.get_component(action_response[target_component])
    return response


class Player:
    def __init__(self, username, uid):
        self.username = username
        self.uid = uid
        self.env = None
        self._socket = None
        self.current_interface = None

        self.awaited_action = None
        self.components = {}

        self._responses = asyncio.Queue()

        self._waiting_messages = []

        self.interfaces = dict()
        self.default_interface = None

    def add_interface(self, interface, is_default=False):
        self.interfaces[interface.name] = interface
        if is_default:
            self.default_interface = interface

    def set_env(self, env):
        self.env = env

    async def update_interface(self, node):
        interface = self.env.bind_interface(node, self)
        await self.switch_interface(interface)

    @property
    def socket(self):
        return self._socket

    @property
    def connected(self):
        return self._socket is not None and not self._socket.closed

    def disconnect(self):
        self._socket = None

    async def connect(self, socket):
        logging.info(f"Connecting {self.uid}.")
        if self._socket is not None:
            await self._socket.close()
        self._socket = socket

        # Send pending messages
        waiting_messages = deepcopy(self._waiting_messages)  # insures that no infinite loop if re deconnects.
        self._waiting_messages = []
        if len(waiting_messages):
            logging.info(f"{self.uid} catching up missing messages.")
        for message in waiting_messages:
            await self.send(message)

    async def switch_interface(self, interface):
        if interface is not self.current_interface:
            if self.current_interface is not None:
                await self.current_interface.unsubscribe_to_components(self)
            self.current_interface = interface
            await interface.subscribe_to_components(self)
        # Then interface
        await self.send({
            "type": "INTERFACE_UPDATE",
            **interface.get_client_update()
        })

    async def components_update(self, components):
        interface = self.current_interface
        transformed_components = interface.transform_components_update(components)

        # Update current info of the components
        for component in transformed_components:
            if component['type'] in ['Create', 'Update']:
                self.components[component['id']] = component['component']
            elif component['type'] == "Delete" and component['id'] in self.components.keys():
                del self.components[component['id']]

        await self.send({
            "type": "COMPONENTS_UPDATES",
            "components": transformed_components
        })

    async def send(self, message):
        """
        Sends a message to the client
        Args:
            message: message to send
        """
        logging.debug(f"{self.uid} sends message.")
        logging.debug(message)

        if self.connected:
            await self._socket.send_json(message)
        else:  # Don't block everyone
            self._waiting_messages.append(message)

    async def notify(self, content, level="info", duration=10):
        """
        Notification for the player
        Args:
            content: content of the message
            level: level of information. (info, warning, error)
            duration: duration the content should stay on (in seconds)
        """
        await self.send({
            'type': 'NOTIFICATION',
            'level': level,
            'duration': duration,
            'content': content
        })

    async def push_response(self, response):
        """
        Receives a message from the client
        Args:
            response:

        Returns:

        """
        await self._responses.put(response)

    async def client_action(self, action, validators=None):
        """
        Asks for a client action from the client
        Args:
            action: if provided, specifies to the client on what component he should act on.
            validators: list of validators to use

        Returns: response
        """
        logging.debug(f"{self.uid} awaiting client response.")

        self.awaited_action = {
            'type': 'ACTION_AWAITED',
            **action
        }

        await self.send(self.awaited_action)

        while True:
            response = await self._responses.get()

            logging.debug(f"{self.uid} received client response.")

            failed = False
            messages = []

            try:
                transformed_response = action_to_components(action, response, self.current_interface)
            except ValueError:
                failed = True
                messages.append("Response format incorrect.")
            else:
                validators = validators or dict()

                for key, sub_response in transformed_response.items():
                    if key in validators:
                        try:
                            transformed_response[key] = validators[key].validate(transformed_response[key])
                        except ValidationException as e:
                            failed = True
                            messages.append(str(e))
                if not failed:
                    break

            if failed:
                logging.debug(f"{self.uid} received bad client response.")
                await self.socket.send_json({"type": "ERROR",
                                             "messages": messages})

        self.awaited_action = None
        return transformed_response
