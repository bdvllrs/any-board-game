import inspect
from copy import copy


class ResponseValidation:
    model = None

    def __init__(self, node):
        self._messages = []
        self.failed = False
        self.node = node

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

    def add_fail_message(self, message):
        self.failed = True
        self.add_message(message)

    def transform_response(self, response, model=None):
        """
        Transforms the response according to the model
        Args:
            response:
            model:

        Returns: transformed response
        """
        model = model or self.model
        if model is None:
            return response
        if type(model) == dict:
            if type(response) != dict:
                self.add_fail_message("The response should be a dict.")
                return response
            for item in model.keys():
                if item not in response:
                    self.add_fail_message(f"Missing item {item} in response.")
                    return response
                response[item] = self.transform_response(response[item], model[item])
            return response
        # If model is a class, we replace the content in the response by an instance of this class
        if inspect.isclass(model):
            signature = inspect.signature(model.__init__)
            args = {}
            for param in list(signature.parameters.values())[1:]:
                # If no default value, we need to provide one
                # If it has a default, then not necessary.
                if param.default == param.empty:
                    if param.name not in response:
                        self.add_fail_message(f"Missing item {param.name} in response.")
                        return response
                if param.name in response:
                    args[param.name] = response[param.name]
            return model(**args)

    def update_response(self, response):
        """
        Additional checks
        Args:
            response

        Returns:
        """
        return response

    def validate(self, response):
        """
        Validates the response
        Args:
            response:

        Returns:

        """
        if "data" not in response:
            self.add_fail_message("Response format incorrect.")
        else:
            response['data'] = self.transform_response(copy(response['data']))
        if not self.failed:
            response['data'] = self.update_response(response['data'])
        return response
