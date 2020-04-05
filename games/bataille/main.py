import numpy as np

from game_engine.game import GameInstance
from game_engine.state import StateManager, StateNode, Triggers


def has_player2_won(env, card1, card2):
    val1, suit1 = card1
    val2, suit2 = card2
    if suit1 == suit2:
        return val1 < val2
    return env['win_round'] == 'player2'


def end_condition(node, env):
    return len(env['cards']['player1']) == 0 or len(env['cards']['player2']) == 0


def swith_player_condition(node, env):
    message = env.client_messages[-1]['selected_card']
    selected_card = (int(message[:-1]), message[-1])
    return selected_card in env['cards'][node.name] and not env['played'] == 0


def resolve_condition(node, env):
    return env['played'] > 0


def resolve_to_player1(node, env):
    return env['win_round'] == 'player1'


def resolve_to_player2(node, env):
    return env['win_round'] == 'player2'


def player_plays(node, env):
    message = env.client_messages[-1].pop()['selected_card']
    card = (int(message[:-1]), message[-1])
    env[node.name + '_card'] = card
    env['cards'][node.name].remove(card)
    env['played'] += 1


def handle_resolve(node, env):
    player2_won = has_player2_won(env, env['player1_card'], env['player2_card'])
    env['win_round'] = 'player2' if player2_won else 'player1'
    env['played'] = 0
    env['win_round'] = None
    env['player1_card'] = None
    env['player2_card'] = None


class BatailleInstance(GameInstance):
    def __init__(self, game_id):
        super().__init__(game_id)

        playing_cards = [str(val) + suit for val in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                         for suit in ["H", "C", "S", "D"]]

        self.state_mng = StateManager()

        self.start_node = StateNode("start", is_initial=True)
        self.end_node = StateNode("end", is_end=True)

        self.player1 = StateNode("player1",
                                 trigger=Triggers.CLIENT_ACTION,
                                 message_backbone=dict(selected_card=dict(IN=playing_cards)))
        self.player2 = StateNode("player2",
                                 trigger=Triggers.CLIENT_ACTION,
                                 message_backbone=dict(selected_card=dict(IN=playing_cards)))
        self.resolve = StateNode("resolve", setup=handle_resolve)

        self.start_node.add_edge(self.player1)

        self.player1.add_edge(self.player2, swith_player_condition,
                              actions=[player_plays])
        self.player1.add_edge(self.resolve, condition=resolve_condition)
        self.player1.add_edge(self.player1)  # if something went wrong

        self.player2.add_edge(self.player1, condition=swith_player_condition,
                              actions=[player_plays])
        self.player2.add_edge(self.resolve, condition=resolve_condition)
        self.player2.add_edge(self.player2)

        self.resolve.add_edge(self.player1, condition=resolve_to_player1)
        self.resolve.add_edge(self.end_node, condition=end_condition)
        self.resolve.add_edge(self.player2, condition=resolve_to_player2)

        self.state_mng.add_states([self.start_node, self.end_node, self.player1, self.player2])

        self.init_card_deck()

    def init_card_deck(self):
        playing_cards = [(val, suit) for val in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
                         for suit in ["H", "C", "S", "D"]]
        np.random.shuffle(playing_cards)
        half_deck = len(playing_cards) // 2

        self.state_mng['cards'] = dict(player1=playing_cards[:half_deck], player2=playing_cards[half_deck:])
        self.state_mng['played'] = 0

    def get_state(self):
        return self.state_mng
