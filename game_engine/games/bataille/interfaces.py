from game_engine.client.components import CardDeckInterfaceComponent
from game_engine.client.interface import Interface


class DefaultInterface(Interface):
    def __init__(self, name, played_cards_deck):
        super().__init__(name)

        self.components = {
            # Cards played by the players during the round
            "played_cards": CardDeckInterfaceComponent("played_cards", played_cards_deck)
        }


class PlayerInterface(DefaultInterface):  # This extends the default interface
    def __init__(self, name, played_cards_deck, hand_card_deck):
        super().__init__(name, played_cards_deck)

        self.add_component(CardDeckInterfaceComponent("hand", hand_card_deck))

