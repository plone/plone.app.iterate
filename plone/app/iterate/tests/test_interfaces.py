# -*- coding: utf-8 -*-
from plone.app.iterate.interfaces import IBaseline
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IIterateAware
from plone.app.iterate.interfaces import IWorkingCopy
from plone.app.iterate.testing import PLONEAPPITERATEDEX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.utils import createContentInContainer
from unittest2 import TestCase


class TestObjectsProvideCorrectInterfaces(TestCase):
    """Since p.a.iterate replaces the baseline on checkin with the working copy
    but p.a.stagingbehavior just copies the values, the provided interfaces
    may be wrong after checkin.

    For making sure that provided interfaces are correct in every state we
    test it here.

    See: https://dev.plone.org/ticket/13163
    """

    layer = PLONEAPPITERATEDEX_INTEGRATION_TESTING

    def setUp(self):
        super(TestObjectsProvideCorrectInterfaces, self).setUp()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        # create a folder where everything of this test suite should happen
        self.assertNotIn('test-folder', self.portal.objectIds())
        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'test-folder'))

        self.obj = createContentInContainer(self.folder, 'Document')

    def tearDown(self):
        self.portal.manage_delObjects([self.folder.id])
        logout()
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        super(TestObjectsProvideCorrectInterfaces, self).tearDown()

    def do_checkout(self):
        policy = ICheckinCheckoutPolicy(self.obj)
        working_copy = policy.checkout(self.folder)
        return working_copy

    def do_cancel(self, working_copy):
        policy = ICheckinCheckoutPolicy(working_copy)
        policy.cancelCheckout()

    def do_checkin(self, working_copy):
        policy = ICheckinCheckoutPolicy(working_copy)
        policy.checkin('')

    def test_before_checkout(self):
        self.assertTrue(self.obj)
        self.assertTrue(IIterateAware.providedBy(self.obj))
        self.assertFalse(IBaseline.providedBy(self.obj))
        self.assertFalse(IWorkingCopy.providedBy(self.obj))

    def test_after_checkout(self):
        working_copy = self.do_checkout()
        self.assertTrue(working_copy)
        self.assertTrue(IIterateAware.providedBy(working_copy))
        self.assertFalse(IBaseline.providedBy(working_copy))
        self.assertTrue(IWorkingCopy.providedBy(working_copy))

        self.assertTrue(IIterateAware.providedBy(self.obj))
        self.assertTrue(IBaseline.providedBy(self.obj))
        self.assertFalse(IWorkingCopy.providedBy(self.obj))

    def test_after_cancel_checkout(self):
        working_copy = self.do_checkout()
        self.assertTrue(working_copy)

        self.do_cancel(working_copy)
        self.assertTrue(IIterateAware.providedBy(self.obj))
        self.assertFalse(IBaseline.providedBy(self.obj))
        self.assertFalse(IWorkingCopy.providedBy(self.obj))

    def test_after_checkin(self):
        working_copy = self.do_checkout()
        self.assertTrue(working_copy)

        self.do_checkin(working_copy)
        self.assertTrue(IIterateAware.providedBy(self.obj))
        self.assertFalse(IBaseline.providedBy(self.obj))
        self.assertFalse(IWorkingCopy.providedBy(self.obj))
