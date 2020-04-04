from game_engine.state import StateManager, StateNode


def add_one_counter_action(node, env):
    env['counter'] = env['counter'] + 1


def test_state_manager():
    stage_mng = StateManager()

    start_state = StateNode("start", is_initial=True)
    end_state = StateNode("end", is_end=True)

    middle_state_1 = StateNode("mid1")
    middle_state_2 = StateNode("mid2")

    start_state.add_edge(middle_state_1)
    middle_state_1.add_edge(middle_state_1,
                            conditions=lambda env: env['counter'] < 2,
                            actions=[add_one_counter_action])
    middle_state_1.add_edge(middle_state_2,
                            conditions=lambda env: env['counter'] >= 2)
    middle_state_2.add_edge(end_state)

    stage_mng.add_states([start_state, end_state, middle_state_1, middle_state_2])
    stage_mng['counter'] = 0

    state_order = []
    for state in stage_mng():
        state_order.append(state.name)

    assert state_order == ["start", "mid1", "mid1", "mid1", "mid2", "end"]
