"""
This file defines the nodes expected contexts.
If the context given to the node does not fit, the State Machine will not execute the transition.
"""
from game_engine.components.cards import Card
from game_engine.validators import ResponseValidation


class PlayResponseValidator(ResponseValidation):
    # This tells the model of the expected response
    # And will transform the message into a Card instance.
    # This means the response should be a JSON object with the argument of the __init__ of the Card object.
    # In this case, {"suit": "S", "value": 5}.

    model = {
        'card': Card
    }

    # This can add additional validations and update the response as wanted
    def update_response(self, response):
        # Current state machine node can be accessed via self.node
        player_uid = self.node.env.state['current_player']
        player_hand = self.node.env.state['hands'][player_uid]
        if response['card'].name not in list(map(lambda card: card.name, player_hand)):
            self.add_fail_message(f"Player does not own this card.")
        return response
