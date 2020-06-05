from any_board_game.client.interface import Interface


class PlayerInterface(Interface):  # This extends the default interface
    def __init__(self, name):
        super().__init__(name)

        self.add_component("played_cards")
        self.add_component("hand")
