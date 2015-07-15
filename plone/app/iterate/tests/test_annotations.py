# -*- coding: utf-8 -*-

import unittest

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IWCContainerLocator
from plone.app.iterate.testing import PLONEAPPITERATEDEX_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapters


class AnnotationsTestCase(unittest.TestCase):

    layer = PLONEAPPITERATEDEX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', 's1')
        self.s1 = self.portal['s1']

    def test_object_annotatable(self):
        self.assertTrue(IAnnotatable.providedBy(self.s1))

    def test_annotation_saved_on_checkin(self):
        # First we get and save a custom annotation to the existing object
        obj_annotations = IAnnotations(self.s1)
        self.assertEqual(obj_annotations, {})

        obj_annotations['key1'] = u'value1'
        obj_annotations = IAnnotations(self.s1)
        self.assertEqual(obj_annotations, {'key1': u'value1'})

        # Now, let's get a working copy for it.
        locators = getAdapters((self.s1,), IWCContainerLocator)
        location = u'plone.app.iterate.parent'
        locator = [c[1] for c in locators if c[0] == location][0]

        policy = ICheckinCheckoutPolicy(self.s1)

        wc = policy.checkout(locator())

        # Annotations should be the same
        new_annotations = IAnnotations(wc)
        self.assertEqual(new_annotations['key1'], u'value1')

        # Now, let's modify the existing one, and create a new one
        new_annotations['key1'] = u'value2'
        new_annotations['key2'] = u'value1'

        # Check that annotations were stored correctly and original ones were
        # not overriten
        new_annotations = IAnnotations(wc)
        self.assertEqual(new_annotations['key1'], u'value2')
        self.assertEqual(new_annotations['key2'], u'value1')

        obj_annotations = IAnnotations(self.s1)
        self.assertEqual(obj_annotations['key1'],  u'value1')
        self.assertFalse('key2' in obj_annotations)

        # Now, we do a checkin
        policy = ICheckinCheckoutPolicy(wc)
        policy.checkin(u'Commit message')

        # And finally check that the old object has the same annotations as
        # its working copy

        obj_annotations = IAnnotations(self.s1)
        self.assertTrue('key1' in obj_annotations)
        self.assertTrue('key2' in obj_annotations)
        self.assertEqual(obj_annotations['key1'], u'value2')
        self.assertEqual(obj_annotations['key2'], u'value1')
