from __future__ import annotations


__all__ = (
    "PreconditionError",
    "PreconditionContext",
    "precondition",
    "TestCase",
)

import contextlib
import functools
from typing import TYPE_CHECKING

from django.db import transaction
from django.test import TestCase as DjangoTestCase


if TYPE_CHECKING:
    from typing import Iterator

from unittest.case import _SubTest


class PreconditionError(AssertionError):
    """Exception to indicate a precondition failure."""

    __precondition_failure__ = True


class PreconditionContext:
    """Context manager to handle precondition failures.

    This context tags every raised :class:`AssertionError` as precondition error.

    .. code-block::

        with PreconditionContext():
             do_something()
    """

    def __enter__(self) -> PreconditionContext:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        with contextlib.suppress(TypeError):
            if issubclass(exc_type, AssertionError):
                exc_val.__precondition_failure__ = True
                raise exc_val
        return False


def precondition(func):
    """Decorator to define a callable as precondition.

    Wraps a callable into a :class:`PreconditionContext`, so that any :class:`AssertionError`
    raised by the callable will lead to a precondition failure rather than a
    failure of the test.

    .. code-block::

        from anfema_django_testutils.testcases import TestCase, precondition


        class CustomTestCase(TestCase):

            @precondition
            def custom_precondition(self):
                do_something()

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with PreconditionContext():
            return func(*args, **kwargs)

    return wrapper


class TestCase(DjangoTestCase):
    """Extends the django TestCase class with a precondition failure status."""

    preconditionFailureException = PreconditionError

    def _feedErrorsToResult(self, result, errors):
        for test, exc_info in errors:
            if isinstance(test, _SubTest):
                result.addSubTest(test.test_case, test, exc_info)
            elif exc_info is not None:
                if issubclass(exc_info[0], (self.failureException, self.preconditionFailureException)):
                    if getattr(exc_info[0], '__precondition_failure__', None):
                        result.addPreconditionFailure(test, exc_info)
                    else:
                        result.addFailure(test, exc_info)
                else:
                    result.addError(test, exc_info)

    @precondition
    def _callSetUp(self):
        super()._callSetUp()

    @classmethod
    @precondition
    def setUpClass(cls):
        """:meta private:"""
        super().setUpClass()

    def fail_precondition(self, msg: str = None):
        """Fail immediately with :class:`PreconditionError`.

        Call this method from a test case if you want to indicate it has
        been finished with precondition failure rather than failure.

        :param str msg: Optional message to use.
        """
        standard_msg = "Precondition failed."
        raise self.preconditionFailureException(self._formatMessage(msg, standard_msg))

    def assertPrecondition(self):
        """Context manager to handle precondition failures.

        Any :class:`AssertionError` or subclass of it, which is raised within the context will
        indicate the test has been finished with precondition failure rather than failure. Any other
        exception type will not be caught, and the test case will be deemed to have suffered an error,
        exactly as for an unexpected exception.

        .. code-block::

           with self.assertPrecondition():
                do_something()

        """
        return PreconditionContext()

    @contextlib.contextmanager
    def assertNotRaises(
        self, *unexpected_exception: Exception, atomic: bool = False, msg: str = None
    ) -> Iterator[None]:
        """Fail if an exception of class *unexpected_exception* is raised by the callable.

        Any other exception type will not be caught, and the test case will be deemed to have
        suffered an error, or, if the exception is from type :class:`AssertionError` a failure
        respectively a precondition error if its from type :class:`PreconditionError`.

        :param Exception \*unexpected_exception: Exception classes expected to not be raised.
        :param bool atomic: If set to :code:`True`, the context will be wrapped inside
          a transaction. Default is :code:`False`.
        :param str msg: Optional message to use on failure.
        """

        try:
            yield transaction.atomic() if atomic else contextlib.nullcontext()
        except unexpected_exception as e:
            standard_msg = f"Unexpected {e.__class__.__name__} raised: {e!r}"
            raise self.fail(self._formatMessage(msg, standard_msg))
