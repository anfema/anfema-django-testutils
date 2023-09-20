"""The :mod:`anfema_django_testutils.contrib.fixtures` app provides to find fixture and fixture media files from each
of your applications and any other specified places.

Settings
========

``FIXTURE_FINDERS``

``FIXTURE_DIRS``

``FIXTURE_MEDIAFILE_FINDERS``

``FIXTURE_MEDIAFILE_DIRS``

Management Commands
===================
:mod:`anfema_django_testutils.contrib.fixtures` exposes three management commands.

findfixture
-----------
*django-admin findfixture FILE [FILE ...]*

Finds the absolute paths for given fixture file(s).

findfixturemedia
----------------
*django-admin findfixturemedia FILE [FILE ...]*

Finds the absolute paths for given fixture media file(s).

collectfixturemedia
-------------------
*django-admin collectfixturemedia*

Collect fixture media files in a single location.
"""
