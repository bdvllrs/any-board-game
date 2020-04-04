class StateManager:
    def __init__(self):
        self.nodes = dict()
        self.initial_state = None
        self.end_state = None
        self.current_state = None

        self.state = dict()

    def __getitem__(self, item):
        return self.state[item]

    def __setitem__(self, key, value):
        self.state[key] = value

    def add_states(self, states):
        for state in states:
            self.add_state(state)

    def add_state(self, state):
        assert state.name not in self.nodes.keys()
        self.nodes[state.name] = state
        if state.is_initial:
            self.initial_state = state.name
        if state.is_end:
            self.end_state = state.name

    def __call__(self):
        assert self.initial_state is not None, "No initial state has been added."
        assert self.end_state is not None, "No end state has been added."
        self.current_state = self.initial_state
        state = self.nodes[self.current_state]
        yield state
        while self.current_state != self.end_state:
            new_state = state(self.state)
            self.current_state = new_state
            state = self.nodes[self.current_state]
            yield state


class StateNode:
    def __init__(self, name, is_initial=False, is_end=False):
        self.name = name
        self.is_initial = is_initial
        self.is_end = is_end
        self.next_states = dict()
        self.actions = dict()
        self.conditions = dict()
        self.next_node = None

    def add_edge(self, next_state, conditions=None, actions=None):
        self.next_states[next_state.name] = next_state
        conditions = conditions or (lambda s: True)
        actions = actions or []
        self.conditions[next_state.name] = conditions
        self.actions[next_state.name] = actions

    def __call__(self, env_state):
        self.next_node = None
        for next_state in self.next_states.values():
            if self.conditions[next_state.name](env_state):
                assert self.next_node is None, f"Several possible paths are available for state {self.name}."
                self.next_node = next_state
        assert self.next_node.name in self.actions.keys()
        for action in self.actions[self.next_node.name]:
            action(self, env_state)
        return self.next_node.name
