import logging
from copy import deepcopy
from typing import Dict, List


class NodeExecutionFailure(Exception):
    """
    Is executed whenever the node functions failed (setup, actions, ...)
    """
    pass


class IncorrectResponse(NodeExecutionFailure):
    pass


class FiniteStateMachine:
    def __init__(self, env):
        self.nodes: Dict[str, Node] = dict()

        self.env = env

        self.current_node_history: List[str] = []
        self._final_node = None
        self.initial_node = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current_node_history[-1] == self._final_node:
            raise StopAsyncIteration

        # To have a first loop before the setting up the first node
        if self.initial_node:
            self.initial_node = False
            return self.current_node_history[0]

        new_node = await self.step()
        return new_node

    def add_node(self, node: 'Node'):
        """
        Add a new node in the state machine
        """
        node.env = self.env
        self.nodes[node.name] = node
        if node.is_initial:
            self.current_node_history.append(node.name)
        if node.is_final:
            self._final_node = node.name

    async def step(self):
        self.env.step_state()
        current_node = self.current_node_history[-1]
        node = self.nodes[current_node]

        try:
            await node.setup()
            new_node = await node.handle()
        except Exception as e:
            logging.exception(e)
            logging.info("Reverting to previous state.")

            # Retry
            # TODO: manage error
            self.revert()
        else:
            self.current_node_history.append(new_node)

        return self.current_node_history[-1]

    def revert(self):
        self.env.revert_state()
        for node in self.nodes.values():
            node.revert()


class Node:
    def __init__(self, name,
                 is_initial=False,
                 is_final=False,
                 setup=None,
                 state=None):
        self.name = name
        self.is_initial = is_initial
        self.is_final = is_final
        self.setup_fn = setup
        self.env = None

        self._original_state = state or dict()
        self.state_history = [self._original_state.copy()]

        self.edges = dict()

    @property
    def state(self):
        return self.state_history[-1]

    def step_state(self):
        copied_state = deepcopy(self.state)
        self.state_history.append(copied_state)

    async def setup(self):
        assert self.env is not None, "Environment is not set."
        logging.info(f"Game {self.env.round_id} node {self.name} setting up.")

        self.step_state()

        if self.setup_fn is not None:
            await self.setup_fn(self)

    def revert(self):
        logging.info(f"Game {self.env.round_id} node {self.name} reverting to previous state.")
        self.state_history.pop()
        if not len(self.state_history):
            self.state_history = [self._original_state.copy()]

    def add_edge(self, next_state_name, condition=None, actions=None):
        actions = actions or []
        self.edges[next_state_name] = dict(condition=condition,
                                           actions=actions)

    async def execute_transition(self):
        next_node = None
        else_node = None
        for next_state_name, next_state in self.edges.items():
            condition = next_state['condition']
            if condition is None:
                assert else_node is None, "There can be only one else condition."
                else_node = next_state_name
            else:
                condition_result = await condition(self)
                if condition_result:
                    assert next_node is None, f"Several possible paths are available for state {self.name}."
                    next_node = next_state_name
        if next_node is None:
            return else_node
        return next_node

    async def handle(self):
        # Validates the parameters

        # Transition
        next_node_name = await self.execute_transition()
        logging.info(f"Game {self.env.round_id} node {self.name} transitioning to {next_node_name}. Executing actions.")
        next_node = self.env.state_machine.nodes[next_node_name]
        for action in self.edges[next_node_name]['actions']:
            await action(self, next_node)
        return next_node_name
