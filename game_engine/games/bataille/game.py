from game_engine.components.cards import CardDeck
from game_engine.games.bataille.card import Card
from game_engine.game import GameEnv
from game_engine.games.bataille.interfaces import PlayerInterface
from game_engine.games.bataille.utils import new_turn_setup, play_node_setup, new_turn_end_condition, \
    play_new_turn_condition, set_player_in_node_state_action, play_new_turn_action
from game_engine.state import Node


class BatailleGame(GameEnv):
    # Here are some game settings
    min_players = 2
    max_players = 4
    game_id = "bataille"  # This is used to start new instances of this game

    def __init__(self, round_id, created_by, is_public):
        # First, always call the super function
        super().__init__(round_id, created_by, is_public)

        # Each GameEnv instance has a self.state attribute containing the state of the game.
        # For everything is self.state, a history is kept, so its value can be freely modified.
        # It is possible to back in time if something goes wrong by calling self.state_machine.revert().
        # This will reset the state contents as it was one step before.
        # General constants can be defined as normal class attributes.
        # Everything that will be changed during the game should be put in self.state.

        # Now we define the cards that will be available.
        # These will stay constant throughout the game.
        self.card_suits = ["H", "C", "S"]
        self.card_numbers = list(map(str, [1, 2]))
        # Here we will create a component CardDeck.
        # Every component should be put in the component registry `self.components` that handles components.
        # We recommend using self.components.create(ComponentClass, *params) to automatically keep track of them.
        self.playing_cards = CardDeck([
            Card(suit + number, state={"suit": suit, "value": number})
            for number in self.card_numbers for suit in self.card_suits
        ])

        self.state['played_cards'] = CardDeck()

        # Now we will build the game as state machine automaton.
        # self.state_machine contains the automaton.
        # We can add nodes to the automaton
        self.state_machine.add_node(Node('start', is_initial=True))
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
        self.state_machine.nodes['new_turn'].add_edge('play', actions=[set_player_in_node_state_action])
        self.state_machine.nodes['new_turn'].add_edge('end',
                                                      condition=new_turn_end_condition)

        self.state_machine.nodes['play'].add_edge('play', actions=[set_player_in_node_state_action])
        # You can also add actions do be done if a certain edge is chosen. Here play_new_turn_action
        # will be called if the state machine goes from play to new_turn
        self.state_machine.nodes['play'].add_edge('new_turn',
                                                  condition=play_new_turn_condition,
                                                  actions=[play_new_turn_action])

    def bind_interface(self, node, player):
        """
        This is called before updating the interface.
        Args:
            node: Current node
            player: interface

        Returns: the id of the next interface to use
        """
        interface = player.interfaces['player'].bind(played_cards=self.state['played_cards'],
                                                     hand=self.state['hands'][player.uid])
        return interface

    async def setup(self):
        # We then define the interfaces for the client
        # Here we define an empty generic card deck for the hand. We will use the "bind_component" method later
        # to bind this component with a real card deck.
        for player in self.players.values():
            player_interface = PlayerInterface("player")
            player.add_interface(player_interface, is_default=True)
        # This will be called when the game starts before executing the state machine.
        # We will here distribute all cards randomly to the players
        # Distribute cards to players
        self.playing_cards.shuffle()
        player_hands = [[] for _ in self.players.keys()]
        for k in range(len(self.playing_cards)):
            player_hands[k % len(self.players)].append(self.playing_cards.pop()[0])
        self.state['hands'] = dict()
        for k, player_id in enumerate(self.players.keys()):
            hand_deck = CardDeck(player_hands[k])
            self.state['hands'][player_id] = hand_deck
