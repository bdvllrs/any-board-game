from game_engine.components.cards import Card as CardComponent


class Card(CardComponent):
    """
    Here we define our card component from the generic CardComponent class.
    """

    def __init__(self, suit: str, value: str):
        assert suit in ['S', 'H', 'D', 'C'], "This suit is incorrect."
        assert 1 <= int(value) <= 13, "This value is incorrect."

        state = dict(suit=suit, value=value)
        super(Card, self).__init__(suit + value, state=state)

    @property
    def suit(self):
        return self.state['suit']

    @property
    def value(self):
        return self.state['value']

    def __gt__(self, other):
        # Compare two cards
        # If same suit, biggest suit wins, otherwise the spade wins
        if self.suit == other.suit:
            return self.value > other.value
        if self.suit == "S":
            return True
        elif other.suit == "S":
            return False
        return self.value > other.value

    def __lt__(self, other):
        return not self.__gt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value
