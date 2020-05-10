from game_engine.components.cards import Card as Card_


class Card(Card_):
    def __gt__(self, other):
        # Compare two cards
        # If same suit, biggest suit wins, otherwise the spade wins
        if self.state['suit'] == other.state['suit']:
            return self.state['value'] > other.state['value']
        if self.state['suit'] == "S":
            return True
        elif other.state['suit'] == "S":
            return False
        return self.state['value'] > other.state['value']

    def __lt__(self, other):
        return not self.__gt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __eq__(self, other):
        return self.state['suit'] == other.state['suit'] and self.state['value'] == other.state['value']
