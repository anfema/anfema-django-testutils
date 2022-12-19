"""This module provides test case tags related utilities."""

__all__ = ('TestCaseTag',)

from django.test import tag


class TestCaseTag:
    """Decorator base class to create predefined test case
    `tags <https://docs.djangoproject.com/en/4.1/topics/testing/tools/#tagging-tests>`_.

    .. versionadded:: 0.2

    With this class you can create re-usable test case tags for your Django project:

    .. code-block::

        class CustomTestCaseTag(TestCaseTag):
            \"\"\"A custom testcase tag\"\"\"
            tags = ['VeryImportantTest', 'VerySlowTest']

        @CustomTestCaseTag('Tag1', 'Tag2')
        class CustomTestCase(TestCase):
            ...

    This is pretty much the same as tagging a test class like:

    .. code-block::

        @tag('CustomTestCaseTag', 'VeryImportantTest', 'VerySlowTest', 'Tag1', 'Tag2')
        class CustomTestCase(TestCase):
                ...

    .. hint::

        If you have several tags to define you can generically use the :class:`TestCaseTag` in a separate module,
        for instance:

        .. code-block::

            # custom_tags.py

            __all__ = ('AdminTest', 'ModelTest', 'FormTest')

            import sys
            from anfema_django_testutils.tags import TestCaseTag

            for tag_name in __all__:
                setattr(sys.modules[__name__], tag_name, type(tag_name, (TestCaseTag,), {}),)

    """

    tags = []
    """A list with predefined extra tags."""

    def __init__(self, *tags):
        self.tags = set(self.tags).union((self.__class__.__name__, *tags))

    def __call__(self, obj):
        return tag(*self.tags)(obj)
