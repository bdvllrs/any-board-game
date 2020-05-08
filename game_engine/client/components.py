class InterfaceComponent:
    def __init__(self, name, visible=True, position='bottom'):
        self.name = name
        self.bound_component = None

        self._state = {
            "type": None,
            "component_name": name,
            "position": position,
            "visible": visible,
        }

    @property
    def state(self):
        state = self._state
        if self.bound_component is not None:
            state.update(self.bound_component.interface_description)
            state['on_action'] = self.bound_component.on_action
            state['type'] = self.bound_component.__class__.__name__

        return state

    def bind(self, component):
        self.bound_component = component

    def unbind(self):
        self.bound_component = None
