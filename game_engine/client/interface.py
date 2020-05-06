class Interface:
    def __init__(self, name):
        self.name = name

        self.components = dict()

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

    def bind_component(self, component_name, component):
        """
        Binds a component with a new one
        Args:
            component_name: name of the component to bind
            component: new component
        """
        assert component_name in self.components, f"{component_name} is not a component."
        self.components[component_name].bind(component)
        return self

    def unbind_component(self, component_name):
        """
        Unbind a given component
        Args:
            component_name: name of the component to unbind
        """
        assert component_name in self.components, f"{component_name} is not a component."
        self.components[component_name].unbind()
        return self

    def get_client_update(self):
        components = dict()
        for component_name in self.components.keys():
            components[component_name] = self.components[component_name].state

        return {"components": components}
