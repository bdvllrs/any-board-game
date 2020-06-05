"""
This file defines the nodes expected contexts.
If the context given to the node does not fit, the State Machine will not execute the transition.
"""
from any_board_game.components.cards import Card
from any_board_game.validators import ResponseValidation, ValidationException


class PlayResponseValidator(ResponseValidation):
    # This tells the model of the expected response
    # And will transform the message into a Card instance.
    # This means the response should be a JSON object with the argument of the __init__ of the Card object.

    model = Card

    # This can add additional validations and update the response as wanted
    def update_response(self, card):
        # Current state machine node can be accessed via self.node
        player_uid = self.node.env.state['current_player']
        player_hand = self.node.env.state['hands'][player_uid]
        if card.name not in map(lambda c: c.name, player_hand.cards):
            raise ValidationException(f"Player does not own this card.")
        return card
