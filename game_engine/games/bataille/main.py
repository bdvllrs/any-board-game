import numpy as np

from game_engine.game import GameInstance
from game_engine.games.bataille.card import Card
from game_engine.games.bataille.response_validations import PlayResponseCondition


def card_comp(card1, card2):
    if card1.suit == card2.suit:
        return card1.value > card2.value
    if card1.suit == "S":
        return True
    elif card2.suit == "S":
        return False
    return card1.value > card2.value


def new_turn_setup(node, env):
    # Remove all played cards
    env.state['played_cards'] = dict()
    players = list(env.players.keys())
    players = [players[-1]] + players[:-1]  # Turn order
    env.state['player_order'] = players


def play_node_action(node, env, player, client_response):
    card = client_response['card']
    env.state['current_player'] = env.state['player_order'].pop()
    env.state['played_cards'][player.uid] = card
    env.state['hands'][player.uid].remove(card)


def new_turn_end_condition(node, env):
    for player in env.players:
        hand = env.state['hands'][player.uid]
        if not len(hand):
            return True
    return False


def play_new_turn_condition(node, env):
    if not len(env.state['player_order']):
        return True
    return False


def play_new_turn_action(node, env):
    card_order = sorted(env.state['played_cards'].items(), key=card_comp)
    loser = card_order[0][0]
    env.state['hands'][loser].extend(list(env.state['played_cards'].values()))


class BatailleGame(GameInstance):
    min_players = 2
    max_players = 4
    game_id = "bataille"

    def __init__(self, game_id, created_by, is_public):
        super().__init__(game_id, created_by, is_public)

        self.card_suits = ["H", "C", "S", "D"]
        self.card_numbers = list(map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))
        self.player_hands = dict()
        self.current_player = None

        self.state_machine.add_node('start', is_initial=True)
        self.state_machine.add_node('end', is_final=True)
        self.state_machine.add_node('new_turn',
                                    setup=new_turn_setup)
        self.state_machine.add_node('play',
                                    trigger="CLIENT_ACTED",
                                    response_validators=[PlayResponseCondition],
                                    actions=[play_node_action])

        self.state_machine.node('start').add_edge('new_turn')

        self.state_machine.node('new_turn').add_edge('play')
        self.state_machine.node('new_turn').add_edge('end',
                                                     condition=new_turn_end_condition)

        self.state_machine.node('play').add_edge('play')
        self.state_machine.node('play').add_edge('new_turn',
                                                 condition=play_new_turn_condition,
                                                 actions=[play_new_turn_action])

    def start(self):
        # Distribute cards to players
        playing_cards = [Card(suit, number) for number in self.card_numbers for suit in self.card_suits]
        np.random.shuffle(playing_cards)
        player_hands = [[] for _ in self.players.keys()]
        for k in range(len(playing_cards)):
            player_hands[k % len(self.players)].append(playing_cards.pop())
        self.state['hands'] = dict()
        for k, player_id in enumerate(self.players.keys()):
            self.state['hands'][player_id] = player_hands[k]

        # Should be at the end
        super(BatailleGame, self).start()

