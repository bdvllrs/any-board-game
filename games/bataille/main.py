import numpy as np

from game_engine.game import GameInstance


def player_node_setup(env, context):
    if context["player_id"] != env.current_player:
        raise C


class BatailleGame(GameInstance):
    def __init__(self, game_id):
        super().__init__(game_id)

        self.card_suits = ["H", "C", "S", "D"]
        self.card_numbers = list(map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]))
        self.player_hands = dict()
        self.current_player = None

        self.state_machine.add_node("start", is_initial=True)
        self.state_machine.add_node("end", is_final=True)
        self.state_machine.add_node("player",
                                    setup=player_node_setup,
                                    context_model={
                                        "selected_card": {
                                            "suit": {"$IN": self.card_suits},
                                            "number": {"$IN": self.card_numbers}
                                        },
                                        "player_id": {"$TYPE": "str"}
                                    })
        self.state_machine.add_node("resolve")

        self.state_machine.nodes['start'].add_edge("player")

        self.state_machine.nodes['player'].add_edge("player")
        self.state_machine.nodes['player'].add_edge("resolve")

        self.state_machine.nodes['resolve'].add_edge("player")
        self.state_machine.nodes['resolve'].add_edge("end")

    def can_add_player(self, player):
        return len(self.players) < 3  # Max 3 players

    def start(self):
        super(BatailleGame, self).start()

        # Distribute cards to players
        playing_cards = [(number, suit) for number in self.card_numbers for suit in self.card_suits]
        np.random.shuffle(playing_cards)
        player_hands = [[] for _ in self.players.keys()]
        for k in range(len(playing_cards)):
            player_hands[k % len(self.players)].append(playing_cards.pop())
        for k, player_id in enumerate(self.players.keys()):
            self.player_hands[player_id] = player_hands[k]

        self.current_player = list(self.players.keys())[0]
