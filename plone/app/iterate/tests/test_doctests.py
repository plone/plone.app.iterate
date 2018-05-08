# -*- coding: utf-8 -*-
from plone.app.iterate.testing import PLONEAPPITERATE_FUNCTIONAL_TESTING
from plone.app.iterate.testing import PLONEAPPITERATEDEX_FUNCTIONAL_TESTING
from plone.testing import layered
from unittest import TestSuite
import doctest

try:
    import Products.ATContentTypes
except ImportError:
    HAS_AT = False
else:
    HAS_AT = True


def test_suite():
    suite = TestSuite()
    OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    if HAS_AT:
        suite.addTest(layered(
            doctest.DocFileSuite(
                'browser.rst',
                optionflags=OPTIONFLAGS,
                package='plone.app.iterate.tests',
            ),
            layer=PLONEAPPITERATE_FUNCTIONAL_TESTING)
        )
    suite.addTest(layered(
        doctest.DocFileSuite(
            'dexterity.rst',
            optionflags=OPTIONFLAGS,
            package='plone.app.iterate.tests',
        ),
        layer=PLONEAPPITERATEDEX_FUNCTIONAL_TESTING)
    )
    return suite
