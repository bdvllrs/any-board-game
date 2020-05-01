class Interface:
    def __init__(self, name):
        self.name = name

        self.components = dict()

        self.component_bindings = dict()

    def add_component(self, component, name=None):
        """
        Add a component
        Args:
            component:
            name: name of the component. Default, component.name
        """
        if name is None:
            name = component.name
        self.components[name] = component

    def get_component(self, component_name):
        """
        Return the component (or bound component)
        Args:
            component_name:

        Returns: component
        """
        assert component_name in self.components, "This component does not exist."
        if component_name in self.component_bindings:
            return self.component_bindings[component_name]
        return self.components[component_name]

    def bind_component(self, component_name, component):
        """
        Binds a component with a new one
        Args:
            component_name: name of the component to bind
            component: new component
        """
        assert component_name in self.components, f"{component_name} is not a component"
        self.component_bindings[component_name] = component
        return self

    def unbind_component(self, component_name):
        """
        Unbind a given component
        Args:
            component_name: name of the component to unbind
        """
        del self.component_bindings[component_name]
        return self

    def get_client_update(self):
        components = dict()
        for component_name in self.components.keys():
            component = self.get_component(component_name)
            components[component_name] = component.state

        return {"components": components}
