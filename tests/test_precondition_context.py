import builtins
import inspect
from contextlib import suppress
from operator import itemgetter
from unittest import TestCase

from anfema_django_testutils.testcases import PreconditionContext


class PreconditionContextTestCase(TestCase):
    def setUp(self) -> None:
        self.precondition_context = PreconditionContext()

    def test_no_exception_raised_in_precondition_context(self):
        """Feature: Precondition Context

        Scenario: No Exception Raised in Precondition Context
            Given a PreconditionContext instance
            When entering the Precondition Context without raising any exceptions
            Then the Precondition Context should exit without any exceptions being raised
        """
        with self.precondition_context:
            pass

    def test_assertion_error_raised_in_precondition_context(self):
        """Feature: Precondition Context

        Scenario: AssertionError Raised in Precondition Context
            Given a PreconditionContext instance
            When entering the Precondition Context and raising an AssertionError
            Then the Precondition Context should raise an AssertionError
            And the AssertionError should have the "__precondition_failure__" attribute set to True
        """
        with self.assertRaises(AssertionError) as cm:
            with self.precondition_context as pcc:
                self.assertIs(self.precondition_context, pcc)
                raise (exception := AssertionError())

        self.assertIs(exception, cm.exception)
        self.assertTrue(hasattr(exception, "__precondition_failure__"))
        self.assertTrue(exception.__precondition_failure__)

    def test_builtin_exception_raised_in_precondition_context(self):
        """Feature: Precondition Context

        Scenario: Built-in Exception Raised in Precondition Context
            Given a PreconditionContext instance
            When entering the Precondition Context and raising various built-in exceptions
            Then the Precondition Context should raise the respective exception types
            And each raised exception should not have the "__precondition_failure__" attribute
        """

        def filter_testable_exceptions(mem):
            with suppress(TypeError):
                is_testable_exception = issubclass(mem, BaseException) and not issubclass(
                    mem, (AssertionError, UnicodeError)
                )
                with suppress(NameError):  # BaseExceptionGroup has been introduced in py3.10
                    is_testable_exception &= not issubclass(mem, BaseExceptionGroup)
                return is_testable_exception
            return False

        for exc_type in map(itemgetter(1), inspect.getmembers(builtins, predicate=filter_testable_exceptions)):
            with self.subTest(exc_type=exc_type.__name__):
                with self.assertRaises(exc_type) as cm:
                    with self.precondition_context as pcc:
                        self.assertIs(self.precondition_context, pcc)
                        raise (exception := exc_type())
                self.assertIs(exception, cm.exception)
                self.assertFalse(hasattr(exception, "__precondition_failure__"))
