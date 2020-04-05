import pytest

from game_engine.state import StateManager, StateNode


def add_one_counter_action(node, env):
    env['counter'] += 1


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
                  condition=lambda node, env: env['counter'] < 2,
                  actions=[add_one_counter_action])
    mid1.add_edge(mid2,
                  condition=lambda node, env: env['counter'] >= 2)
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng.execute():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid1", "mid1", "mid2", "end"]


def test_state_else_condition():
    stage_mng, start_state, end_state, mid1, mid2 = init_states()

    start_state.add_edge(mid1)
    mid1.add_edge(mid1,
                  condition=lambda node, env: env['counter'] < 2,
                  actions=[add_one_counter_action])
    mid1.add_edge(mid2)  # If no condition, will be used as an "else" condition
    mid2.add_edge(end_state)

    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng.execute():
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
        for state in stage_mng.execute():
            state_order.append(state.name)
