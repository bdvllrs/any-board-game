from copy import deepcopy as copy


class NodeExecutionFailure(Exception):
    """
    Is executed whenever the node functions failed (setup, actions, ...)
    """
    pass


class ContextIncorrect(NodeExecutionFailure):
    pass


class FiniteStateMachine:
    def __init__(self, env):
        self.nodes = [dict()]

        self.env_history = [copy(env)]

        self.current_node_history = []
        self._final_node = None

    def node(self, name):
        return self.nodes[-1][name]

    def add_node(self, name,
                 is_initial=False,
                 is_final=False,
                 setup=None,
                 state=None,
                 context_validators=None):
        node = Node(name, is_initial, is_final, setup, state, context_validators)
        self.nodes[0][node.name] = node
        if node.is_initial:
            self.current_node_history.append(node.name)
        if node.is_final:
            self._final_node = node.name

    def step(self, context=None):
        nodes = copy(self.nodes[-1])
        env = copy(self.env_history[-1])
        self.nodes.append(nodes)
        self.env_history.append(env)

        current_node = self.current_node_history[-1]

        node = nodes[current_node]
        node.env = env
        try:
            node.context = context
            node.setup()
            new_node_name = node.handle()
        except NodeExecutionFailure as e:
            print("Node failed to execute: ", str(e))
            print("Reverting to previous state.")

            self.current_node_history.append(current_node)
            self.revert()

            node.response = dict(error=True, message="Context incorrect.")
        else:
            self.current_node_history.append(new_node_name)
        return node.response

    def revert(self):
        self.nodes.pop()
        self.env_history.pop()
        self.current_node_history.pop()


class Node:
    def __init__(self, name,
                 is_initial=False,
                 is_final=False,
                 setup=None,
                 state=None,
                 context_validators: list = None):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
        self.setup_fn = setup
        self.state = state
        self.context_validators = context_validators or []
        self.env = None
        self._context = None

        self.response = None

        self.edges = dict()

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        for validator in self.context_validators:
            if not validator.validate(copy(self), copy(context), copy(self.env)):
                raise ContextIncorrect(validator.get_message())
        self._context = context

    def setup(self):
        self.response = None
        if self.setup_fn is not None:
            self.setup_fn(self, self.env)

    def add_edge(self, next_state_name, condition=None, actions=None):
        actions = actions or []
        self.edges[next_state_name] = dict(condition=condition,
                                           actions=actions)

    def execute_transition(self):
        next_node = None
        else_node = None
        for next_state_name, next_state in self.edges.items():
            condition = next_state['condition']
            if condition is None:
                assert else_node is None, "There can be only one else condition."
                else_node = next_state_name
            elif condition(copy(self), copy(self.env)):
                assert next_node is None, f"Several possible paths are available for state {self.name}."
                next_node = next_state_name
        if next_node is None:
            return else_node
        return next_node

    def handle(self):
        new_node = self.execute_transition()
        for action in self.edges[new_node]['actions']:
            action(self, self.env)
        return new_node
