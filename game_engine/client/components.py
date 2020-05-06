class InterfaceComponent:
    def __init__(self, name, component, visible=True, position='bottom'):
        self.name = name
        self.component = component
        self.bound_component = None

        self._state = {
            "type": component.__class__.__name__,
            "component_name": name,
            "position": position,
            "visible": visible,
        }

    @property
    def state(self):
        state = self._state
        component = self.bound_component if self.bound_component is not None else self.component
        state.update(component.interface_description)
        state['on_action'] = component.on_action

        return state

    def bind(self, component):
        self.bound_component = component

    def unbind(self):
        self.bound_component = None
