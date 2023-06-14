from __future__ import annotations


__all__ = (
    "PreconditionError",
    "PreconditionContext",
    "precondition",
    "SimpleTestCase",
    "TransactionTestCase",
    "TestCase",
)

import contextlib
import functools
from typing import TYPE_CHECKING

from django.db import transaction
from django.test import SimpleTestCase as DjangoSimpleTestCase
from django.test import TestCase as DjangoTestCase
from django.test import TransactionTestCase as DjangoTransactionTestCase


if TYPE_CHECKING:
    from typing import Iterator


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


class TestCaseMixin:
    preconditionFailureException = PreconditionError

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
        self, *unexpected_exception: type[Exception], atomic: bool = False, msg: str = None
    ) -> Iterator[None]:
        """Fail if an exception of class *unexpected_exception* is raised by the callable.

        Any other exception type will not be caught, and the test case will be deemed to have
        suffered an error, or, if the exception is from type :class:`AssertionError` a failure
        respectively a precondition error if its from type :class:`PreconditionError`.

        :param type[Exception] \*unexpected_exception: Exception classes expected to not be raised.
        :param bool atomic: If set to :code:`True`, the context will be wrapped inside
          a transaction. Default is :code:`False`.
        :param str msg: Optional message to use on failure.
        """

        try:
            yield transaction.atomic() if atomic else contextlib.nullcontext()
        except unexpected_exception as e:
            standard_msg = f"Unexpected {e.__class__.__name__} raised: {e!r}"
            raise self.fail(self._formatMessage(msg, standard_msg))


class SimpleTestCase(TestCaseMixin, DjangoSimpleTestCase):
    """Extends the :class:`django.test.SimpleTestCase` class with a precondition failure status.
    """


class TransactionTestCase(TestCaseMixin, DjangoTransactionTestCase):
    """Extends the :class:`django.test.TransactionTestCase` class with a precondition failure status.

    .. seealso:: :class:`SimpleTestCase`
    """


class TestCase(TestCaseMixin, DjangoTestCase):
    """Extends the :class:`django.test.TestCase` class with a precondition failure status.

    .. seealso:: :class:`SimpleTestCase`
    """
