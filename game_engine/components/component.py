import asyncio
import inspect
import uuid


class Component:
    def __init__(self, interface_state: dict = None):
        self.id = uuid.uuid4().hex
        interface_state = interface_state or {}

        self.interface_state = {
            'position': 'center'
        }

        self.interface_state.update(interface_state)

        self.subscribers = {}

    async def subscribe(self, player, on_create=True):
        """
        Adds a player to the list of subscribed player of this component.
        Args:
            player:
            on_create: if true, will send an on_create event
        """
        self.subscribers[player.uid] = player
        for component in self.get_sub_components():
            if component is not self:
                await component.subscribe(player, False)
        # Setup
        if on_create:
            await self.on_create([player])

    async def unsubscribe(self, player, on_delete=True):
        if player.uid in self.subscribers:
            del self.subscribers[player.uid]
        for component in self.get_sub_components():
            if component is not self:
                await component.unsubscribe(player, False)
        # Cleanup
        if on_delete:
            await self.on_delete([player])

    async def on_create(self, subscribers=None):
        components = []
        for component in self.get_sub_components():
            component_description = component.interface_description
            components.append({
                'type': 'Create',
                'id': component.id,
                'component': component_description
            })
        await self.on_change(components, subscribers)

    async def on_change(self, components, subscribers=None):
        subscribers = subscribers or self.subscribers.values()
        await asyncio.gather(*[player.components_update(components)
                               for player in subscribers])

    async def on_update(self, subscribers=None):
        components = [{
            'type': 'Update',
            'id': self.id,
            'component': self.interface_description
        }]
        await self.on_change(components, subscribers)

    async def on_delete(self, subscribers=None):
        await self.on_change([{
            'type': 'Delete',
            'id': self.id
        }], subscribers)

    def get_sub_components(self):
        """
        Returns: component and all subcomponents
        """
        return [self]

    def _get_component_description(self):
        description = dict()
        signature = inspect.signature(self.__init__)
        for param in list(signature.parameters.values()):
            if param.name != 'interface_state' and hasattr(self, param.name):
                description[param.name] = getattr(self, param.name)
        description['type'] = self.__class__.__name__
        return description

    @property
    def interface_description(self):
        return self._get_component_description()
