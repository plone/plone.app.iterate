from plone.app.iterate.testing import PLONEAPPITERATEDEX_FUNCTIONAL_TESTING
from plone.testing import layered
from unittest import TestSuite

import doctest


def test_suite():
    suite = TestSuite()
    OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    suite.addTest(
        layered(
            doctest.DocFileSuite(
                "dexterity.rst",
                optionflags=OPTIONFLAGS,
                package="plone.app.iterate.tests",
            ),
            layer=PLONEAPPITERATEDEX_FUNCTIONAL_TESTING,
        )
    )
    return suite
