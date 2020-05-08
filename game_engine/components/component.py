import inspect


class Component:
    @property
    def interface_description(self):
        description = dict()
        signature = inspect.signature(self.__init__)
        for param in list(signature.parameters.values()):
            if hasattr(self, param.name):
                description[param.name] = getattr(self, param.name)
        return description

    @property
    def on_action(self):
        on_action = dict()
        component_state = self.interface_description
        signature = inspect.signature(self.__init__)

        for param in list(signature.parameters.values()):
            if param.name in component_state.keys():
                on_action[param.name] = f"$component.{param.name}"
        return on_action
