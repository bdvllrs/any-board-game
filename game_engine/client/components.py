class InterfaceComponent:
    def __init__(self, name, on_action=None, visible=True, position='bottom'):
        self.name = name

        self.state = {
            "position": position,
            "visible": visible,
            "on_action": on_action
        }


class CardInterfaceComponent(InterfaceComponent):
    def __init__(self, name, card, *params, **kwargs):
        super(CardInterfaceComponent, self).__init__(name, *params, **kwargs)

        self.card = card


class CardDeckInterfaceComponent(InterfaceComponent):
    def __init__(self, name, card_deck, *params, **kwargs):
        super(CardDeckInterfaceComponent, self).__init__(name, *params, **kwargs)

        self.card_deck = card_deck
