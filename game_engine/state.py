from copy import deepcopy as copy


class ContextIncorrect(Exception):
    pass

def correct_context(context_model, context):
    if context_model is None:
        return context is None
    for key, model in context_model.items():
        if key == "$IN":
            if key == "$IN" and context not in model:
                return False
        else:
            if key not in context.keys():
                return False
            if not correct_context(model, context[key]):
                return False
    return True


class FiniteStateMachine:
    def __init__(self, env):
        self.nodes = [dict()]

        self.env_history = [copy(env)]

        self.current_node_history = []
        self._final_node = None

    def add_node(self, name,
                 is_initial=False,
                 is_final=False,
                 setup=None,
                 state=None,
                 context_model=None):
        node = Node(name, is_initial, is_final, setup, state, context_model)
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
        is_context_correct = correct_context(node.context_skeleton, context)
        if is_context_correct:
            try:
                node.setup(env, context)
            except ContextIncorrect:
                is_context_correct = False
            else:
                new_node_name = node.handle(env, context)
                self.current_node_history.append(new_node_name)
        if not is_context_correct:
            self.current_node_history.append(current_node)
            node.response = dict(error=True, message="Context incorrect.")
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
                 context_model=None):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
        self.setup_fn = setup
        self.state = state

        self.context_model = context_model

        self.response = None

        self.edges = dict()

    def setup(self, env, context):
        self.response = None
        if self.setup_fn is not None:
            self.setup_fn(env, context)

    def add_edge(self, next_state_name, condition=None, actions=None):
        actions = actions or []
        self.edges[next_state_name] = dict(condition=condition,
                                           actions=actions)

    def execute_transition(self, env, context):
        next_node = None
        else_node = None
        for next_state_name, next_state in self.edges.items():
            condition = next_state['condition']
            if condition is None:
                assert else_node is None, "There can be only one else condition."
                else_node = next_state_name
            elif condition(copy(self), copy(env), copy(context)):
                assert next_node is None, f"Several possible paths are available for state {self.name}."
                next_node = next_state_name
        if next_node is None:
            return else_node
        return next_node

    def handle(self, env, context):
        new_node = self.execute_transition(env, context)
        for action in self.edges[new_node]['actions']:
            action(self, env, copy(context))
        return new_node
