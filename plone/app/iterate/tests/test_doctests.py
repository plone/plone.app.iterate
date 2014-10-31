# -*- coding: utf-8 -*-
import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite

from plone.app.iterate.tests.test_iterate import IterateFunctionalTestCase


def test_suite():
    suite = TestSuite()
    OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    suite.addTest(
        FunctionalDocFileSuite(
            'browser.rst',
            optionflags=OPTIONFLAGS,
            package="plone.app.iterate.tests",
            test_class=IterateFunctionalTestCase,
        ),
    )
    return suite
