from game_engine.client.components import CardDeckInterfaceComponent
from game_engine.client.interface import Interface


class DefaultInterface(Interface):
    def __init__(self, name, played_cards_deck):
        super().__init__(name)

        self.components = {
            # Cards played by the players during the round
            "played_cards": CardDeckInterfaceComponent("played_cards", played_cards_deck)
        }
