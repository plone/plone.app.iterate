# -*- coding: utf-8 -*-
##################################################################
#
# (C) Copyright 2006 ObjectRealms, LLC
# All Rights Reserved
#
# This file is part of iterate.
#
# iterate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# iterate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iterate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################

from AccessControl import getSecurityManager
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.testing import PLONEAPPITERATEDEX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from zc.relation.interfaces import ICatalog
from zope.intid.interfaces import IIntIds
from zope import component

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

    @unittest.skip('This test needs to be fixed for Dexterity content.')
    def test_workflowState(self):
        # ensure baseline workflow state is retained on checkin, including
        # security

        doc = self.portal.docs.doc1

        # sanity check that owner can edit visible docs
        setRoles(self.portal, TEST_USER_ID, ['Owner'])
        self.assertTrue(getSecurityManager().checkPermission(
            'Modify portal content', self.portal.docs.doc1))

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.wf.doActionFor(doc, 'publish')
        state = self.wf.getInfoFor(doc, 'review_state')

        self.repo.save(doc)
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        wc_state = self.wf.getInfoFor(wc, 'review_state')

        self.assertNotEqual(state, wc_state)

        ICheckinCheckoutPolicy(wc).checkin('modified')
        bstate = self.wf.getInfoFor(wc, 'review_state')
        self.assertEqual(state, bstate)
        setRoles(self.portal, TEST_USER_ID, ['Owner'])

    def test_baselineVersionCreated(self):
        # if a baseline has no version ensure that one is created on checkout

        doc = self.portal.docs.doc1
        self.assertTrue(self.repo.isVersionable(doc))

        history = self.repo.getHistory(doc)
        self.assertEqual(len(history), 0)

        ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)

        history = self.repo.getHistory(doc)
        self.assertEqual(len(history), 1)

        doc2 = self.portal.docs.doc2
        self.repo.save(doc2)

        ICheckinCheckoutPolicy(doc2).checkout(self.portal.workarea)

        history = self.repo.getHistory(doc2)
        self.assertEqual(len(history), 1)

    def test_folderOrder(self):
        """When an item is checked out and then back in, the original
        folder order is preserved."""
        container = self.portal.docs
        doc = container.doc1
        original_position = container.getObjectPosition(doc.getId())

        # check that there is another document which could interact with
        # position of document the test work on
        doc2_position = container.getObjectPosition('doc2')
        self.assertTrue(doc2_position > original_position)

        self.repo.save(doc)
        wc = ICheckinCheckoutPolicy(doc).checkout(container)
        wc.text = 'new document text'

        # check that the copy is put after the second document
        copy_position = container.getObjectPosition(wc.getId())
        self.assertTrue(copy_position > doc2_position)

        new_doc = ICheckinCheckoutPolicy(wc).checkin('updated')
        new_position = container.getObjectPosition(new_doc.getId())
        self.assertEqual(new_position, original_position)

    @unittest.skip('This test needs to be fixed for Dexterity content.')
    def test_folderContents(self):
        """When an folder is checked out, and item is added, and then
        the folder is checked back in, the added item is in the new
        version of the folder.  UIDs of contained content are also
        preserved."""
        container = self.portal.docs
        folder = container[container.invokeFactory(
            type_name='Folder', id='foo-folder')]
        existing_doc = folder[folder.invokeFactory(
            type_name='Document', id='existing-folder-item')]
        existing_doc_uid = existing_doc.UID()

        self.repo.save(folder)
        wc = ICheckinCheckoutPolicy(folder).checkout(container)
        new_doc = wc[wc.invokeFactory(type_name='Document',
                                      id='new-folder-item',
                                      text='new folder item text')]
        new_doc_uid = new_doc.UID()
        new_folder = ICheckinCheckoutPolicy(wc).checkin('updated')

        catalog = getToolByName(self.portal, 'portal_catalog')

        self.assertTrue('existing-folder-item' in new_folder)
        self.assertEqual(
            new_folder['existing-folder-item'].UID(), existing_doc_uid)
        self.assertTrue('new-folder-item' in new_folder)
        self.assertEqual(new_folder['new-folder-item'].UID(), new_doc_uid)
        brains = catalog(path='/'.join(
            new_folder['new-folder-item'].getPhysicalPath()))
        self.assertTrue(brains)
        self.assertTrue('new folder item text' in
                        new_folder['new-folder-item'].getText())

    def test_default_page_is_kept_in_folder(self):
        # Ensure that a default page that is checked out and back in is still
        # the default page.
        folder = self.portal.docs
        doc = folder.doc1
        from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault  # noqa: C901
        ISelectableBrowserDefault(folder).setDefaultPage('doc1')
        self.assertEqual(folder.getProperty('default_page', ''), 'doc1')
        self.assertEqual(folder.getDefaultPage(), 'doc1')
        # Note: when checking out to self.portal.workarea it surprisingly works
        # without changes.  But the default behavior in Plone is to check a
        # document out in its original folder, so that is what we check here.
        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        doc = ICheckinCheckoutPolicy(wc).checkin('updated')
        self.assertEqual(folder.getProperty('default_page', ''), 'doc1')
        self.assertEqual(folder.getDefaultPage(), 'doc1')

    def test_control_checkin_allowed_with_no_policy(self):
        control = Control(self.portal, self.layer['request'])
        self.assertFalse(control.checkin_allowed())

    def test_control_checkout_allowed_with_no_policy(self):
        control = Control(self.portal, self.layer['request'])
        self.assertFalse(control.checkout_allowed())

    def test_control_cancel_allowed_with_no_policy(self):
        control = Control(self.portal, self.layer['request'])
        self.assertFalse(control.cancel_allowed())

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

    def test_relationship_deleted_on_checkin(self):
        # Ensure that the relationship between the baseline and the wc is
        # removed when the working copy is checked in
        folder = self.portal.docs
        doc = folder.doc1

        intids = component.getUtility(IIntIds)
        catalog = component.getUtility(ICatalog)
        obj_id = intids.getId(doc)
        rels = list(catalog.findRelations({'from_id': obj_id}))
        self.assertEqual(len(rels), 0)

        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        wc_id = intids.getId(wc)

        rels = list(catalog.findRelations({'from_id': obj_id}))
        self.assertEqual(len(rels), 1)
        from_rel = rels[0]

        rels = list(catalog.findRelations({'to_id': wc_id}))
        self.assertEqual(len(rels), 1)
        to_rel = rels[0]

        self.assertEqual(from_rel, to_rel)

        doc = ICheckinCheckoutPolicy(wc).checkin('updated')

        rels = list(catalog.findRelations({'from_id': obj_id}))

        self.assertEqual(len(rels), 0)

    def test_relationship_deleted_on_cancel_checkout(self):
        # Ensure that the relationship between the baseline and the wc is
        # removed when the working copy is checked in
        folder = self.portal.docs
        doc = folder.doc1

        intids = component.getUtility(IIntIds)
        catalog = component.getUtility(ICatalog)
        obj_id = intids.getId(doc)
        rels = list(catalog.findRelations({'from_id': obj_id}))
        self.assertEqual(len(rels), 0)

        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        wc_id = intids.getId(wc)

        rels = list(catalog.findRelations({'from_id': obj_id}))
        self.assertEqual(len(rels), 1)
        from_rel = rels[0]

        rels = list(catalog.findRelations({'to_id': wc_id}))
        self.assertEqual(len(rels), 1)
        to_rel = rels[0]

        self.assertEqual(from_rel, to_rel)

        ICheckinCheckoutPolicy(wc).cancelCheckout()

        rels = list(catalog.findRelations({'from_id': obj_id}))

        self.assertEqual(len(rels), 0)
