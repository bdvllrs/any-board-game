from copy import deepcopy


class ValidationException(Exception):
    pass


class ResponseValidation:
    model = None

    def __init__(self, node):
        self.failed = False
        self.node = node

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
        out_response = deepcopy(response)
        out_response = self.update_response(out_response)
        return out_response
