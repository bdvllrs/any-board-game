from game_engine.client.components import InterfaceComponent
from game_engine.client.interface import Interface


class PlayerInterface(Interface):  # This extends the default interface
    def __init__(self, name):
        super().__init__(name)

        self.add_component(InterfaceComponent("played_cards"))
        self.add_component(InterfaceComponent("hand"))
