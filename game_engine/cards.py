class Card:
    def __init__(self, name):
        self.name = name


class CardDeck:
    def __init__(self, from_yaml=None):
        self.cards = None

    def import_yaml(self, path):
        pass
