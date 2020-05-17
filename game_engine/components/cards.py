import asyncio

import numpy as np

from game_engine.components.component import Component


class Card(Component):
    def __init__(self, name: str,
                 description: str = "",
                 front_image: str = None,
                 back_image: str = None,
                 state=None,
                 interface_state=None):
        super().__init__(interface_state)
        self.back_image = back_image
        self.front_image = front_image
        self.description = description
        self.name = name
        self.state = state or dict()


class CardDeck(Component):
    def __init__(self, cards=None, from_yaml=None, interface_state=None):
        super().__init__(interface_state)
        self.cards = cards or []
        if from_yaml is not None:
            self.import_yaml(from_yaml)

        self.card_type = None
        if len(self.cards):
            self.card_type = self.cards[0].__class__
            self.check_card_type(self.cards)

    def check_card_type(self, cards):
        card_type = self.card_type if self.card_type is not None else cards[0].__class__
        if card_type is not None:
            for card in cards:
                if not isinstance(card, card_type):
                    raise ValueError(f"All cards should have the same type {card_type}")

    def get_sub_components(self):
        components = [self]
        for card in self.cards:
            components.extend(card.get_sub_components())
        return components

    @property
    def interface_description(self):
        return {'cards': [card.id for card in self.cards]}

    def import_yaml(self, path):
        # TODO: import cards from yaml file
        raise NotImplementedError

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]

    def __contains__(self, item):
        return item in self.cards

    async def shuffle(self):
        """
        Shuffles the deck
        """
        np.random.shuffle(self.cards)
        await self.on_update()

    async def pop(self, rank=0, n=1):
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
        cards = await self.pop(rank, n - 1)
        cards.append(self.cards.pop(cur_rank))
        await self.on_update()
        await asyncio.gather(*[card.on_delete() for card in cards])
        return cards

    async def add(self, cards):
        """
        Add cards to the deck
        Args:
            cards: list of cards
        """
        self.check_card_type(cards)
        self.cards.extend(cards)

        for card in cards:
            await asyncio.gather(*[card.subscribe(subscriber) for subscriber in self.subscribers.values()])
        await self.on_update()

    async def remove(self, c):
        for card in self.cards:
            if card == c:
                await card.on_delete()
                self.cards.remove(card)
        await self.on_update()
