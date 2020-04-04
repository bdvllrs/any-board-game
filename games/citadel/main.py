from game_engine.state import StateManager, StateNode
from games.citadel.conditions import pick_card_condition, start_used_power_condition, start_picked_coin_condition, \
    used_power_picked_coin_condition, used_power_drew_card_condition, picked_coin_used_power_condition, \
    picked_coin_built_condition, drew_card_used_power_condition, drew_card_built_condition, \
    playing_end_playing_start_condition, building_selection_start_condition

if __name__ == '__main__':
    start_node = StateNode("start", is_initial=True)
    end_node = StateNode("end", is_end=True)

    selection_start_node = StateNode("selection.start")
    pick_card_node = StateNode("selection.pick_card")
    selection_end_node = StateNode("selection.end")

    building_start_node = StateNode("building.start")
    building_end_node = StateNode("building.end")

    playing_start_node = StateNode("playing.start")
    playing_used_power_node = StateNode("playing.used_power")
    playing_picked_coin_node = StateNode("playing.picked_coin")
    playing_drew_card_node = StateNode("playing.drew_card")
    playing_built_node = StateNode("playing.built")
    playing_end_node = StateNode("playing.end")

    start_node.add_edge(selection_start_node)

    selection_start_node.add_edge(pick_card_node)
    pick_card_node.add_edge(pick_card_node, condition=pick_card_condition)
    pick_card_node.add_edge(selection_end_node)

    selection_end_node.add_edge(building_start_node)
    building_start_node.add_edge(playing_start_node)

    playing_start_node.add_edge(playing_used_power_node,
                                condition=start_used_power_condition)
    playing_start_node.add_edge(playing_picked_coin_node,
                                condition=start_picked_coin_condition)
    playing_start_node.add_edge(playing_end_node)

    playing_used_power_node.add_edge(playing_picked_coin_node,
                                     condition=used_power_picked_coin_condition)
    playing_used_power_node.add_edge(playing_drew_card_node,
                                     condition=used_power_drew_card_condition)

    playing_picked_coin_node.add_edge(playing_used_power_node,
                                      condition=picked_coin_used_power_condition)
    playing_picked_coin_node.add_edge(playing_built_node,
                                      condition=picked_coin_built_condition)
    playing_picked_coin_node.add_edge(playing_end_node)

    playing_drew_card_node.add_edge(playing_used_power_node,
                                    condition=drew_card_used_power_condition)
    playing_drew_card_node.add_edge(playing_built_node,
                                    condition=drew_card_built_condition)
    playing_drew_card_node.add_edge(playing_end_node)

    playing_built_node.add_edge(playing_used_power_node)

    playing_built_node.add_edge(playing_start_node,
                                condition=playing_end_playing_start_condition)

    playing_built_node.add_edge(playing_end_node)

    playing_end_node.add_edge(building_end_node)
    building_end_node.add_edge(selection_start_node,
                               condition=building_selection_start_condition)
    building_end_node.add_edge(end_node)

    state_mng = StateManager()
    state_mng.add_states([start_node, end_node, selection_start_node, pick_card_node, selection_end_node,
                          building_start_node, building_end_node, playing_start_node, playing_used_power_node,
                          playing_picked_coin_node, playing_drew_card_node, playing_built_node, playing_end_node,
                          playing_end_node])

    state_mng['current_player'] = state_mng.players[0]
    state_mng['seen_players'] = []
