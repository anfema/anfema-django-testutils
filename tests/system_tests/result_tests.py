from unittest import expectedFailure, skip

from anfema_django_testutils.testcases import TestCase


class ResultTests(TestCase):
    """Tests to check the test results and exit codes"""

    def test_success(self):
        pass

    @skip("")
    def test_skip(self):
        pass

    @expectedFailure
    def test_expected_failure(self):
        self.fail()

    def test_precondition_failure(self):
        self.fail_precondition()

    def test_failure(self):
        self.fail()

    @expectedFailure
    def test_unexpected_success(self):
        pass

    def test_error(self):
        raise ValueError()

    def test_subtest_success(self):
        with self.subTest():
            pass

    @expectedFailure
    def test_subtest_expected_failure(self):
        with self.subTest():
            self.fail()

    def test_subtest_precondition_failure(self):
        with self.subTest():
            self.fail_precondition()

    def test_subtest_failure(self):
        with self.subTest():
            self.fail()

    @expectedFailure
    def test_subtest_unexpected_success(self):
        with self.subTest():
            pass

    def test_subtest_error(self):
        with self.subTest():
            raise ValueError()


class SetupFailPreconditionFailure(TestCase):
    """Tests to check the test results and exit codes"""

    def setUp(self) -> None:
        self.fail_precondition('A precondition is not fulfilled.')

    def test_setup_precondition_failure(self):
        pass  # Dummy test routine should not be executed.


class SetupTestDataAssertionFails(TestCase):
    """Tests to check the test results and exit codes"""

    @classmethod
    def setUpTestData(cls):
        assert False, 'A precondition is not fulfilled.'

    def test_setup_test_data_assertion_fails(self):
        pass  # Dummy test routine should not be executed.


class SetupTestDataError(TestCase):
    """Tests to check the test results and exit codes"""

    @classmethod
    def setUpTestData(cls):
        raise ValueError('A precondition is not fulfilled.')

    def test_setup_test_data_error(self):
        pass  # Dummy test routine should not be executed.
