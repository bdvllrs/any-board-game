class ResponseValidation:
    def __init__(self):
        self._messages = []
        self._has_failed = False

    def get_message(self):
        return "\n".join(self._messages)

    def add_message(self, message):
        """
        Add a new error message.
        Args:
            message:

        Returns:

        """
        self._messages.append(message)

    def fail(self, message):
        self._has_failed = True
        self.add_message(message)

    def validate(self, node, env, *params, **kwargs):
        """
        Checks that the context is correct.
        Args:
            node: checked node
            env:

        Returns (bool): whether the context is correct
        """
        # TODO
        self.add_message("")  # Adds a new message
        return True
