from copy import deepcopy as copy


class NodeExecutionFailure(Exception):
    """
    Is executed whenever the node functions failed (setup, actions, ...)
    """
    pass


class ResponseIncorrect(NodeExecutionFailure):
    pass


class FiniteStateMachine:
    def __init__(self, env):
        self.nodes = [dict()]

        self.env_history = [copy(env)]

        self.current_node_history = []
        self._final_node = None

    def node(self, name):
        return self.nodes[-1][name]

    def add_node(self, *params, **kwargs):
        node = Node(*params, **kwargs)
        self.nodes[0][node.name] = node
        if node.is_initial:
            self.current_node_history.append(node.name)
        if node.is_final:
            self._final_node = node.name

    def step_setup(self):
        nodes = copy(self.nodes[-1])
        env = copy(self.env_history[-1])
        self.nodes.append(nodes)
        self.env_history.append(env)

        current_node = self.current_node_history[-1]

        node = nodes[current_node]
        node.env = env
        try:
            node.setup()
        except NodeExecutionFailure as e:
            print("Node failed to execute: ", str(e))
            print("Reverting to previous state.")

            # Retry
            # TODO: add error callback on states, and manage error
            self.node_execution_failed()
        else:
            env.event_manager.register(node.trigger,
                                       self.step_resolve,
                                       self.node_execution_failed,
                                       condition=node.trigger_condition)
            env.event_manager.trigger("NODE_SETUP")

    def step_resolve(self, *params, **kwargs):
        nodes = self.nodes[-1]
        env = self.env_history[-1]
        current_node = self.current_node_history[-1]

        node = nodes[current_node]
        node.env = env

        try:
            node.handle(*params, **kwargs)
        except NodeExecutionFailure as e:
            print("Node failed to execute: ", str(e))
            print("Reverting to previous state.")

            self.node_execution_failed()
        else:
            env.event_manager.register("NODE_EXITED", self.step_setup)
            env.event_manager.trigger("NODE_EXITED")

    def node_execution_failed(self, *params, **kwargs):
        env = self.env_history[-1]
        self.revert()
        env.event_manager.register("NODE_EXECUTION_FAILED", self.step_setup)
        env.event_manager.trigger("NODE_EXECUTION_FAILED")

    def revert(self):
        if len(self.nodes) == len(self.env_history) == len(self.current_node_history):
            self.current_node_history.pop()
        if len(self.nodes) == len(self.env_history):
            self.nodes.pop()
            self.env_history.pop()


class Node:
    def __init__(self, name,
                 is_initial=False,
                 is_final=False,
                 setup=None,
                 state=None,
                 trigger="NODE_SETUP",
                 trigger_condition=None,
                 response_validators: list = None,
                 actions=None):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
        self.setup_fn = setup
        self.state = state
        self.trigger = trigger
        self.trigger_condition = trigger_condition
        self.response_validators = response_validators or []
        self.actions = actions
        self.env = None

        self.response = None

        self.edges = dict()

    def setup(self):
        self.response = None
        if self.setup_fn is not None:
            self.setup_fn(self, self.env)

    def add_edge(self, next_state_name, condition=None, actions=None):
        actions = actions or []
        self.edges[next_state_name] = dict(condition=condition,
                                           actions=actions)

    def execute_transition(self, *params, **kwargs):
        next_node = None
        else_node = None
        for next_state_name, next_state in self.edges.items():
            condition = next_state['condition']
            if condition is None:
                assert else_node is None, "There can be only one else condition."
                else_node = next_state_name
            elif condition(copy(self), copy(self.env), *params, **kwargs):
                assert next_node is None, f"Several possible paths are available for state {self.name}."
                next_node = next_state_name
        if next_node is None:
            return else_node
        return next_node

    def handle(self, *params, **kwargs):
        # Validates the parameters
        for validator in self.response_validators:
            if not validator.validate(copy(self), copy(self.env), *params, **kwargs):
                raise ResponseIncorrect(validator.get_message())

        # Internal node actions
        if self.actions is not None:
            for action in self.actions:
                action(self, self.env, *params, **kwargs)

        # Transition
        new_node = self.execute_transition(*params, **kwargs)
        for action in self.edges[new_node]['actions']:
            action(self, self.env, *params, **kwargs)
        return new_node
