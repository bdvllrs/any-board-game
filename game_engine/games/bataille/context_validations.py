"""
This file defines the nodes expected contexts.
If the context given to the node does not fit, the State Machine will not execute the transition.
"""
from game_engine.cards import Card
from game_engine.players import Player
from game_engine.validators import ContextValidation


class PlayContextCondition(ContextValidation):
    # First we define what the context should contain.
    model = {
        "player": Player,  # player doing the action
        "card": Card  # card played
    }

    # Then we can define additional checks on the values of the context.
    def check(self, node, context, env):
        if context['player'].uid != env.state['player_order'][-1]:
            self.fail("Player id is incorrect.")

        player_hand = env.state['hands'][context['player'].uid]
        if context['card'].name not in list(map(lambda card: card.name, player_hand)):
            self.fail(f"Player does not own this card.")
