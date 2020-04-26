"""
This file defines the nodes expected contexts.
If the context given to the node does not fit, the State Machine will not execute the transition.
"""
from game_engine.cards import Card
from game_engine.validators import ResponseValidation


class PlayResponseValidator(ResponseValidation):
    # This tells the model of the expected response
    model = {
        'card': Card
    }

    # This can add additional validations
    def check(self, node, response):
        player_uid = node.env.state['current_player']
        player_hand = node.env.state['hands'][player_uid]
        if response['card'].name not in list(map(lambda card: card.name, player_hand)):
            self.fail(f"Player does not own this card.")
