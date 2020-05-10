class Interface:
    def __init__(self, name):
        self.name = name

        self.component_names = []
        self.components = {}
        self.comp_id_to_name = {}

    @property
    def sub_components(self):
        components = []
        for component in self.components.values():
            components.extend(component.get_sub_components())
        return components

    def bind(self, **kwargs):
        for component_name, component in kwargs.items():
            self._bind_component(component_name, component)
        return self

    def add_component(self, component_name):
        """
        Add a component
        Args:
            component_name: name of the component. Default, component.name
        """
        self.component_names.append(component_name)

    def _bind_component(self, component_name, component):
        """
        Binds a component with a new one
        Args:
            component_name: name of the component to bind
            component: new component
        """
        assert component_name in self.component_names, f"{component_name} is not a component."
        self.components[component_name] = component
        self.comp_id_to_name[component.id] = component_name
        return self

    def get_components_update(self):
        components = []
        for component in self.sub_components:
            component_description = component.interface_description
            component_id = component.id
            if component_id in self.comp_id_to_name:
                component_id = self.comp_id_to_name[component_id]

            component_description['type'] = component.__class__.__name__
            components.append({
                'type': 'Create',
                'id': component_id,
                'component': component_description
            })
        return components

    def get_component(self, component_id):
        """
        Returns the component having the given component_id
        Args:
            component_id:
        Returns:
        """
        if component_id in self.components:
            return self.components[component_id]
        for component in self.sub_components:
            if component.id == component_id:
                return component
        raise ValueError

    def get_client_update(self):
        components = []
        for component_name, component in self.components.items():
            state = component.interface_state
            state['id'] = component_name
            components.append(state)

        return {"components": components}
