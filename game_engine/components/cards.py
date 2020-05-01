import numpy as np


class Card:
    def __init__(self, name: str,
                 description: str = "",
                 front_image: str = None,
                 back_image: str = None,
                 state=None):
        self.back_image = back_image
        self.front_image = front_image
        self.description = description
        self.name = name
        self.state = state or dict()


class CardDeck:
    def __init__(self, cards=None, from_yaml=None):
        self.cards = cards or []
        if from_yaml is not None:
            self.import_yaml(from_yaml)

    def import_yaml(self, path):
        # TODO: import cards from yaml file
        raise NotImplementedError

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]

    def shuffle(self):
        """
        Shuffles the deck
        """
        np.random.shuffle(self.cards)

    def pop(self, rank=0, n=1):
        """
        pop cards
        Args:
            rank: rank in the deck to pick the cards from. Can be a list of ranks. In this case, the list should have n
              elements and the first item will be the rank of the first picked card.
            n: number of cards to pick

        Returns: a list of cards
        """
        if n == 'all':
            n = len(self)
        assert len(self.cards) >= n, "Not enough cards in the deck."
        if type(rank) == int:
            rank = [rank] * n
        assert len(rank) == n, "The rank list should have n element."

        if n == 0:
            return []

        cur_rank = rank.pop(0)
        cards = self.pop(rank, n - 1)
        cards.append(self.cards.pop(cur_rank))
        return cards

    def add(self, cards):
        """
        Add cards to the deck
        Args:
            cards: list of cards
        """
        self.cards.extend(cards)

    def remove(self, c):
        for card in self.cards:
            if card == c:
                self.cards.remove(card)
