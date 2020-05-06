from game_engine.validators import ResponseValidation


class ClassTest:
    def __init__(self, expected1, expected2, optional=1):
        self.expected1 = expected1
        self.expected2 = expected2
        self.optional = optional


class ValidatorTest(ResponseValidation):
    model = {
        'test': ClassTest
    }

    # This can add additional validations
    def update_response(self, response):
        if response['test'].expected2 > response['test'].expected1:
            self.add_fail_message(f"Arguments are wrong.")
        return response


def test_simple_validation_wrong_response_type():
    validator = ValidatorTest(None)
    response = {"data": []}
    updated_response = validator.validate(response)

    assert validator.failed
    assert validator.get_message() == "The response should be a dict."


def test_simple_validation_wrong_response_keys():
    validator = ValidatorTest(None)
    response = {"data": {'testing': {'expected1': None, 'expected2': None, 'optional': None}}}
    updated_response = validator.validate(response)

    assert validator.failed
    assert validator.get_message() == "Missing item test in response."


def test_simple_validation_wrong_response_missing_expected_key():
    validator = ValidatorTest(None)
    response = {"data": {'test': {'expected1': None, 'optional': None}}}
    updated_response = validator.validate(response)

    assert validator.failed
    assert validator.get_message() == "Missing item expected2 in response."


def test_simple_validation_update_response_failure():
    validator = ValidatorTest(None)
    response = {"data": {'test': {'expected1': 1, 'expected2': 2, 'optional': 3}}}
    updated_response = validator.validate(response)

    assert validator.failed
    assert validator.get_message() == "Arguments are wrong."


def test_simple_validation_success_with_optional():
    validator = ValidatorTest(None)
    response = {"data": {'test': {'expected1': 2, 'expected2': 1, 'optional': 3}}}
    updated_response = validator.validate(response)['data']

    assert not validator.failed
    assert isinstance(updated_response['test'], ClassTest)
    assert updated_response['test'].expected1 == response['data']['test']['expected1']
    assert updated_response['test'].optional == response['data']['test']['optional']


def test_simple_validation_success_without_optional():
    validator = ValidatorTest(None)
    response = {"data": {'test': {'expected1': 2, 'expected2': 1}}}
    updated_response = validator.validate(response)['data']

    assert not validator.failed
    assert isinstance(updated_response['test'], ClassTest)
    assert updated_response['test'].expected1 == response['data']['test']['expected1']
    assert updated_response['test'].optional == 1
