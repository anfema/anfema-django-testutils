from unittest import TestCase

from anfema_django_testutils.testcases import PreconditionError


class PreconditionErrorTestCase(TestCase):
    def test_precondition_error_has_precondition_failure_attribute(self):
        """Feature: Precondition Error

        Scenario: PreconditionError Has "__precondition_failure__" Attribute
            Given a PreconditionError instance
            Then it should have the "__precondition_failure__" attribute
            And the "__precondition_failure__" attribute should be set to True
        """
        self.assertTrue(precondition_failure := hasattr(PreconditionError(), "__precondition_failure__"))
        self.assertTrue(precondition_failure)
