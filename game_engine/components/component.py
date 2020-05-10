import inspect
import uuid
from copy import deepcopy


class ComponentRegistry:
    def __init__(self):
        self.components = {}

    def create(self, component_class, *params, **kwargs):
        component = component_class(*params, **kwargs)
        self.update(component)
        return component.id

    def update(self, component):
        self.components[component.id] = component

    def get_component_copy(self, component_id):
        return deepcopy(self.components[component_id])


class Component:
    def __init__(self, interface_state: dict = None):
        self.id = uuid.uuid4().hex
        interface_state = interface_state or {}

        self.interface_state = {
            'position': 'center'
        }

        self.interface_state.update(interface_state)

    async def on_create(self):
        pass

    async def on_update(self):
        pass

    async def on_delete(self):
        pass

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
        return description

    @property
    def interface_description(self):
        return self._get_component_description()
