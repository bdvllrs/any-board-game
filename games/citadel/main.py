from game_engine.state import StateManager, StateNode, Triggers
from games.citadel.conditions import pick_card_condition, start_used_power_condition, start_picked_coin_condition, \
    used_power_picked_coin_condition, used_power_drew_card_condition, picked_coin_used_power_condition, \
    picked_coin_built_condition, drew_card_used_power_condition, drew_card_built_condition, \
    playing_end_playing_start_condition, building_selection_start_condition


class CitadelInstance:
    def __init__(self):
        self.start_node = StateNode("start", is_initial=True)
        self.end_node = StateNode("end", is_end=True)

        self.selection_start_node = StateNode("selection.start")
        self.pick_card_node = StateNode("selection.pick_card")
        self.selection_end_node = StateNode("selection.end")

        self.building_start_node = StateNode("building.start")
        self.building_end_node = StateNode("building.end")

        self.playing_start_node = StateNode("playing.start")
        self.playing_used_power_node = StateNode("playing.used_power")
        self.playing_picked_coin_node = StateNode("playing.picked_coin")
        self.playing_drew_card_node = StateNode("playing.drew_card")
        self.playing_built_node = StateNode("playing.built")
        self.playing_end_node = StateNode("playing.end")

        self.start_node.add_edge(self.selection_start_node)

        self.selection_start_node.add_edge(self.pick_card_node)
        self.pick_card_node.add_edge(self.pick_card_node,
                                     condition=pick_card_condition,
                                     trigger=Triggers.CLIENT_ACTION)
        self.pick_card_node.add_edge(self.selection_end_node)

        self.selection_end_node.add_edge(self.building_start_node)
        self.building_start_node.add_edge(self.playing_start_node)

        self.playing_start_node.add_edge(self.playing_used_power_node,
                                         condition=start_used_power_condition)
        self.playing_start_node.add_edge(self.playing_picked_coin_node,
                                         condition=start_picked_coin_condition)
        self.playing_start_node.add_edge(self.playing_end_node)

        self.playing_used_power_node.add_edge(self.playing_picked_coin_node,
                                              condition=used_power_picked_coin_condition)
        self.playing_used_power_node.add_edge(self.playing_drew_card_node,
                                              condition=used_power_drew_card_condition)

        self.playing_picked_coin_node.add_edge(self.playing_used_power_node,
                                               condition=picked_coin_used_power_condition)
        self.playing_picked_coin_node.add_edge(self.playing_built_node,
                                               condition=picked_coin_built_condition)
        self.playing_picked_coin_node.add_edge(self.playing_end_node)

        self.playing_drew_card_node.add_edge(self.playing_used_power_node,
                                             condition=drew_card_used_power_condition)
        self.playing_drew_card_node.add_edge(self.playing_built_node,
                                             condition=drew_card_built_condition)
        self.playing_drew_card_node.add_edge(self.playing_end_node)

        self.playing_built_node.add_edge(self.playing_used_power_node)

        self.playing_built_node.add_edge(self.playing_start_node,
                                         condition=playing_end_playing_start_condition)

        self.playing_built_node.add_edge(self.playing_end_node)

        self.playing_end_node.add_edge(self.building_end_node)
        self.building_end_node.add_edge(self.selection_start_node,
                                        condition=building_selection_start_condition)
        self.building_end_node.add_edge(self.end_node)

        self.state_mng = StateManager()
        self.state_mng.add_states(
            [self.start_node, self.end_node, self.selection_start_node, self.pick_card_node, self.selection_end_node,
             self.building_start_node, self.building_end_node, self.playing_start_node, self.playing_used_power_node,
             self.playing_picked_coin_node, self.playing_drew_card_node, self.playing_built_node,
             self.playing_end_node])

        self.state_mng['current_player'] = self.state_mng.players[0]
        self.state_mng['seen_players'] = []
