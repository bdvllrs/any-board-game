import pytest

from game_engine.state import StateManager, StateNode


def add_one_counter_action(node, env):
    env['counter'] += 1


def add_one_counter_action_and_re_route(node, env):
    env['counter'] += 1
    node.next_node = 'mid2'  # re-routing


def init_states():
    stage_mng = StateManager()

    start_state = StateNode("start", is_initial=True)
    end_state = StateNode("end", is_end=True)

    mid1 = StateNode("mid1")
    mid2 = StateNode("mid2")

    stage_mng.add_states([start_state, end_state, mid1, mid2])

    return stage_mng, start_state, end_state, mid1, mid2


def test_state_manager():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()

    start_state.add_edge(mid1)
    # Conditions are checked BEFORE actions are executed.
    mid1.add_edge(mid1,
                  condition=lambda env: env['counter'] < 2,
                  actions=[add_one_counter_action])
    mid1.add_edge(mid2,
                  condition=lambda env: env['counter'] >= 2)
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid1", "mid1", "mid2", "end"]


def test_state_else_condition():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()

    start_state.add_edge(mid1)
    mid1.add_edge(mid1,
                  condition=lambda env: env['counter'] < 2,
                  actions=[add_one_counter_action])
    mid1.add_edge(mid2)  # If no condition, will be used as an "else" condition
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid1", "mid1", "mid2", "end"]
    assert stage_mng['counter'] == 2


def test_state_two_else_condition():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()

    start_state.add_edge(mid1)
    mid1.add_edge(mid1,
                  actions=[add_one_counter_action])
    mid1.add_edge(mid2)
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    with pytest.raises(AssertionError):
        for state in stage_mng():
            state_order.append(state.name)


def test_change_routing_in_action():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()

    start_state.add_edge(mid1)
    mid1.add_edge(mid1,
                  condition=lambda env: env['counter'] < 2,
                  actions=[add_one_counter_action_and_re_route])  # This action re routes the state order.
    # This shows that routing can also be done via the actions.
    mid1.add_edge(mid2)  # If no condition, will be used as an "else" condition
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid2", "end"]
    assert stage_mng['counter'] == 1


def route_mid1(node, env):
    if env['counter'] < 2:
        node.next_node = 'mid1'
    else:
        node.next_node = 'mid2'


def test_route_by_actions():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()
    start_state.add_edge(mid1)
    # Use end_state as fallback state if no other route has been chosen in actions.
    mid1.add_edge(end_state, actions=[route_mid1, add_one_counter_action])
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid1", "mid1", "mid2", "end"]
    assert stage_mng['counter'] == 3
