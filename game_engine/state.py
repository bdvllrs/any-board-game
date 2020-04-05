from enum import Enum


class Triggers(Enum):
    CLIENT_ACTION = "CLIENT_ACTION"


class StateManager:
    def __init__(self):
        self.nodes = dict()
        self.initial_state = None
        self.end_state = None
        self.current_state = None

        self.state = dict()
        self.players = []
        self.client_messages = []

    def get_graph(self):
        nodes = []
        edges = []
        for node_name, node in self.nodes.items():
            nodes.append(dict(name=node_name,
                              is_initial=node.is_initial,
                              is_end=node.is_end,
                              trigger=node.trigger,
                              message_backbone=node.message_backbone))
            for next_node_name, next_node in node.next_states.items():
                edges.append(dict(node_start=node_name,
                                  node_end=next_node_name))
        return dict(nodes=nodes, edges=edges)

    def __getitem__(self, item):
        return self.state[item]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __contains__(self, item):
        return item in self.state

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
            if state.trigger == Triggers.CLIENT_ACTION:
                # await client message
                # client_message = None
                self.client_messages.append(None)
                pass
            new_state = state.handle(self.state)
            self.current_state = new_state
            state = self.nodes[self.current_state]
            yield state


class StateNode:
    def __init__(self, name, is_initial=False, is_end=False, setup=None, trigger=None, message_backbone=None):
        self.name = name
        self.is_initial = is_initial
        self.is_end = is_end
        self.setup = setup
        self.next_states = dict()
        self.actions = dict()
        self.conditions = dict()
        self.trigger = trigger
        self.message_backbone = message_backbone
        self.next_node = None

    def add_edge(self, next_state, condition=None, actions=None):
        self.next_states[next_state.name] = next_state
        condition = condition
        actions = actions or []
        self.conditions[next_state.name] = condition
        self.actions[next_state.name] = actions

    def handle(self, env_state):
        if self.setup is not None:
            self.setup(self, env_state)
        next_node = None
        else_node = None
        for next_state in self.next_states.values():
            condition = self.conditions[next_state.name]
            if condition is None:
                assert else_node is None, "There can be only one else condition."
                else_node = next_state
            elif condition(self, env_state):
                assert next_node is None, f"Several possible paths are available for state {self.name}."
                next_node = next_state.name
        if next_node is None:
            next_node = else_node.name
        assert next_node in self.actions.keys()
        for action in self.actions[next_node]:
            action(self, env_state)
        return next_node
