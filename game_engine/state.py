import copy
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

    def execute(self):
        assert self.initial_state is not None, "No initial state has been added."
        assert self.end_state is not None, "No end state has been added."
        self.current_state = self.initial_state
        state = self.nodes[self.current_state]
        yield state
        while self.current_state != self.end_state:
            to_yield = get_next_state(state, self)
            can_continue = True
            state_copy = copy.deepcopy(self)
            while can_continue and to_yield != self.end_state:
                new_state = get_next_state(copy.deepcopy(self.nodes[to_yield]), state_copy)
                if self.nodes[new_state].trigger == Triggers.CLIENT_ACTION:
                    can_continue = False
                else:
                    to_yield = get_next_state(self.nodes[to_yield], self)

            self.current_state = to_yield
            state = self.nodes[self.current_state]
            yield state


def get_next_state(node, env_state):
    node.status = ""
    node.error = False
    if node.trigger == Triggers.CLIENT_ACTION:
        if not correct_client_message(node.message_backbone, env_state.client_messages[-1]):
            node.error = True
            node.status = "The message received from the client is not correct."
            return node.name  # We stay in the same state
    if node.setup is not None:
        node.setup(node, copy.deepcopy(env_state))
    next_node = None
    else_node = None
    for next_state in node.next_states.values():
        condition = node.conditions[next_state.name]
        if condition is None:
            assert else_node is None, "There can be only one else condition."
            else_node = next_state
        elif condition(node, env_state):
            assert next_node is None, f"Several possible paths are available for state {node.name}."
            next_node = next_state.name
    if next_node is None:
        next_node = else_node.name
    return next_node


def correct_client_message(message_backbone, client_message):
    for key, backbone in message_backbone.items():
        if key == "$IN":
            if key == "$IN" and client_message not in backbone:
                return False
        else:
            if key not in client_message.keys():
                return False
            if not correct_client_message(backbone, client_message[key]):
                return False
    return True


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
        self.status = ""
        self.error = False

    def add_edge(self, next_state, condition=None, actions=None):
        self.next_states[next_state.name] = next_state
        condition = condition
        actions = actions or []
        self.conditions[next_state.name] = condition
        self.actions[next_state.name] = actions

    def do_actions(self, next_node, env_state):
        assert next_node in self.actions.keys()
        for action in self.actions[next_node]:
            action(self, env_state)
