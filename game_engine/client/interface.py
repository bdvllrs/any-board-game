class Interface:
    def __init__(self, name):
        self.name = name

        self.components = dict()

    def add_component(self, component):
        self.components[component.name] = component
