import numpy as np

from game_engine.game import GameEnv
from game_engine.games.bataille.card import Card
from game_engine.games.bataille.response_validations import PlayResponseValidator
from game_engine.state import Node


def card_comp(card1, card2):
    # Compare two cards
    # If same suit, biggest suit wins, otherwise the spade wins
    if card1.suit == card2.suit:
        return card1.value > card2.value
    if card1.suit == "S":
        return True
    elif card2.suit == "S":
        return False
    return card1.value > card2.value


async def new_turn_setup(node):
    # This method sets up a new turn.
    # You can access the GameEnv instance with node.env
    # First, we will define the played cards of this turn by an empty dict
    node.env.state['played_cards'] = dict()
    # Then we define the order of play
    players = list(node.env.players.keys())
    # the first player in the previous turn will be last to play
    players = players[1:] + [players[0]]
    # And we add it to the state
    node.env.state['player_order'] = players
    node.env.state['current_player'] = players[0]


async def play_node_setup(node):
    # We will use this setup to block the automaton and wait for a player response.
    # First, the get the player whose turn it is
    player_uid = node.env.state['current_player']
    player = node.env.players[player_uid]
    # We will now await a response from that player
    # Note that we added a validator. This will then wait for a specific response from the client.
    # This validator checks that the given card is owned by the player
    response = await player.response(validators=[PlayResponseValidator(node)])
    card = response['card']

    # Now we update the order of play and current player
    node.env.state['current_player'] = node.env.state['player_order'].pop()
    node.env.state['played_cards'][player_uid] = card
    # And we remove the card from the hand of the player.
    node.env.state['hands'][player.uid].remove(card)


async def new_turn_end_condition(node):
    # We go the end node if someone has played all his cards
    for player_uid in node.env.players:
        hand = node.env.state['hands'][player_uid]
        if not len(hand):
            return True
    return False


async def play_new_turn_condition(node):
    # We do a new turn if the player_order list is empty.
    if not len(node.env.state['player_order']):
        return True
    return False


async def play_new_turn_action(node):
    # If we do a new turn, we need to find who won the turn
    card_order = sorted(node.env.state['played_cards'].items(), key=card_comp)
    loser = card_order[0][0]  # the one with lowest card loses and gets the cards of all other players
    node.env.state['hands'][loser].extend(list(node.env.state['played_cards'].values()))


class BatailleGame(GameEnv):
    # Here are some game settings
    min_players = 2
    max_players = 4
    game_id = "bataille"  # This is used to start new instances of this game

    def __init__(self, game_id, created_by, is_public):
        # First, always call the super function
        super().__init__(game_id, created_by, is_public)

        # Each GameEnv instance has a self.state attribute containing the state of the game.
        # For everything is self.state, a history is kept, so its value can be freely modified.
        # It is possible to back in time if something goes wrong by calling self.state_machine.revert().
        # This will reset the state contents as it was one step before.
        # General constants can be defined as normal class attributes.
        # Everything that will be changed during the game should be put in self.state.

        # Now we define the cards that will be available.
        # These will stay constant throughout the game.
        self.card_suits = ["H", "C", "S", "D"]
        self.card_numbers = list(map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]))

        # Now we will build the game as state machine automaton.
        # self.state_machine contains the automaton.
        # We can add nodes to the automaton
        self.state_machine.add_node(Node('start', is_initial=True))  # this node will be the initial node
        # Whenever the final node is reached, the game will finish
        self.state_machine.add_node(Node('end', is_final=True))
        # For this node, a setup callback is added. This callback will
        # be called every time the state machine enters this node.
        self.state_machine.add_node(Node('new_turn',
                                         setup=new_turn_setup))
        self.state_machine.add_node(Node('play',
                                         setup=play_node_setup))

        # Now we define how the transitions between the nodes are done
        # We can do this with the Node.add_edge method.
        self.state_machine.nodes['start'].add_edge('new_turn')

        # We will add two edges from new_turn to play and end.
        # The route will be decided with the condition parameter.
        # If a condition is met, then it will route to this node
        # If no condition is met, the default one will be the edge without condition.
        self.state_machine.nodes['new_turn'].add_edge('play')
        self.state_machine.nodes['new_turn'].add_edge('end',
                                                      condition=new_turn_end_condition)

        self.state_machine.nodes['play'].add_edge('play')
        # You can also add actions do be done if a certain edge is chosen. Here play_new_turn_action
        # will be called if the state machine goes from play to new_turn
        self.state_machine.nodes['play'].add_edge('new_turn',
                                                  condition=play_new_turn_condition,
                                                  actions=[play_new_turn_action])

    async def setup(self):
        # This will be called when the game starts before executing the state machine.
        # We will here distribute all cards randomly to the players
        # Distribute cards to players
        playing_cards = [Card(suit, number) for number in self.card_numbers for suit in self.card_suits]
        np.random.shuffle(playing_cards)
        player_hands = [[] for _ in self.players.keys()]
        for k in range(len(playing_cards)):
            player_hands[k % len(self.players)].append(playing_cards.pop())
        self.state['hands'] = dict()
        for k, player_id in enumerate(self.players.keys()):
            self.state['hands'][player_id] = player_hands[k]
