# -*- coding: utf-8 -*-
from plone.app.iterate.testing import PLONEAPPITERATEDEX_INTEGRATION_TESTING
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME

import unittest


class TestIterations(unittest.TestCase):

    layer = PLONEAPPITERATEDEX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.wf = self.portal.portal_workflow
        self.wf.setChainForPortalTypes(('Document',), 'plone_workflow')

        # add a folder with two documents in it
        self.portal.invokeFactory('Folder', 'docs')
        self.portal.docs.invokeFactory('Document', 'doc1')
        self.portal.docs.invokeFactory('Document', 'doc2')

        # add a working copy folder
        self.portal.invokeFactory('Folder', 'workarea')

        self.repo = self.portal.portal_repository

    def test_control_cancel_on_original_does_not_delete_original(self):
        # checkout document
        doc = self.portal.docs.doc1
        policy = ICheckinCheckoutPolicy(self.portal.docs.doc1, None)
        policy.checkout(self.portal.workarea)

        # get cancel browser view
        from plone.app.iterate.browser.cancel import Cancel
        cancel = Cancel(doc, self.layer['request'])
        self.layer['request'].form['form.button.Cancel'] = True

        # check if cancel on original raises the correct exception
        from plone.app.iterate.interfaces import CheckoutException
        with self.assertRaises(CheckoutException):
            cancel()
