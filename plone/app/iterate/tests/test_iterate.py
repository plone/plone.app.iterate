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

from DateTime import DateTime
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.testing import PLONEAPPITERATEDEX_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import ILockable
from zc.relation.interfaces import ICatalog
from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.intid.interfaces import IIntIds

import unittest


class TestIterations(unittest.TestCase):
    """Test plone.app.iterate on non-folderish items."""

    layer = PLONEAPPITERATEDEX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

        self.wf = self.portal.portal_workflow
        self.wf.setChainForPortalTypes(("Document",), "plone_workflow")

        # add a folder with two documents in it
        self.portal.invokeFactory("Folder", "docs")
        self.portal.docs.invokeFactory("Document", "doc1")
        self.portal.docs.invokeFactory("Document", "doc2")

        # add a working copy folder
        self.portal.invokeFactory("Folder", "workarea")

        self.repo = self.portal.portal_repository

    def get_control_view(self, doc):
        # Remove any memoized items from the request.
        # Especially, we may have memoized 'cancel_allowed'.
        request = self.layer["request"]
        IAnnotations(request).pop("plone.memoize", None)
        return Control(doc, request)

    def test_baselineVersionCreated(self):
        # if a baseline has no version ensure that one is created on checkout
        self.assertIn("Document", self.repo.getVersionableContentTypes())

        doc = self.portal.docs.doc1
        self.assertTrue(self.repo.isVersionable(doc))

        history = self.repo.getHistory(doc)
        self.assertEqual(len(history), 0)

        ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)

        history = self.repo.getHistory(doc)
        self.assertEqual(len(history), 1)

        doc2 = self.portal.docs.doc2
        history = self.repo.getHistory(doc2)
        self.assertEqual(len(history), 0)
        self.repo.save(doc2)
        history = self.repo.getHistory(doc2)
        self.assertEqual(len(history), 1)

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
        doc2_position = container.getObjectPosition("doc2")
        self.assertTrue(doc2_position > original_position)

        self.repo.save(doc)
        wc = ICheckinCheckoutPolicy(doc).checkout(container)
        wc.text = "new document text"

        # check that the copy is put after the second document
        copy_position = container.getObjectPosition(wc.getId())
        self.assertTrue(copy_position > doc2_position)

        new_doc = ICheckinCheckoutPolicy(wc).checkin("updated")
        new_position = container.getObjectPosition(new_doc.getId())
        self.assertEqual(new_position, original_position)

    def test_default_page_is_kept_in_folder(self):
        # Ensure that a default page that is checked out and back in is still
        # the default page.
        folder = self.portal.docs
        doc = folder.doc1
        from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault

        ISelectableBrowserDefault(folder).setDefaultPage("doc1")
        self.assertEqual(folder.getProperty("default_page", ""), "doc1")
        self.assertEqual(folder.getDefaultPage(), "doc1")
        # Note: when checking out to self.portal.workarea it surprisingly works
        # without changes.  But the default behavior in Plone is to check a
        # document out in its original folder, so that is what we check here.
        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        doc = ICheckinCheckoutPolicy(wc).checkin("updated")
        self.assertEqual(folder.getProperty("default_page", ""), "doc1")
        self.assertEqual(folder.getDefaultPage(), "doc1")

    def test_control_document(self):
        # A Document is both versionable and lockable.
        doc = self.portal.docs.doc1
        self.assertIn("Document", self.repo.getVersionableContentTypes())
        self.assertTrue(self.repo.isVersionable(doc))
        try:
            lockable = ILockable(doc)
        except TypeError:
            lockable = False
        self.assertTrue(lockable)

        # Initially of course you can only check-out.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertTrue(control.checkout_allowed())

        # Make a checkout.  Now you can only check-in or cancel.
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        control = self.get_control_view(wc)
        self.assertTrue(control.checkin_allowed())
        self.assertTrue(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

        # On the original you cannot do anything now, because there is a working copy.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

    def test_control_news_item(self):
        # A News Item is both versionable and lockable.
        self.portal.invokeFactory("News Item", "news1")
        doc = self.portal.news1
        self.assertIn("News Item", self.repo.getVersionableContentTypes())
        self.assertTrue(self.repo.isVersionable(doc))
        try:
            lockable = ILockable(doc)
        except TypeError:
            lockable = False
        self.assertTrue(lockable)

        # Initially of course you can only check-out.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertTrue(control.checkout_allowed())

        # Make a checkout.  Now you can only check-in or cancel.
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        control = self.get_control_view(wc)
        self.assertTrue(control.checkin_allowed())
        self.assertTrue(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

        # On the original you cannot do anything now, because there is a working copy.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

    def test_control_locked_document(self):
        doc = self.portal.docs.doc1
        ILockable(doc).lock()

        # Now you can do nothing.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

        # After unlock, you can check-out again.
        ILockable(doc).unlock()
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertTrue(control.checkout_allowed())

        # Make a checkout and lock it.
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        ILockable(wc).lock()
        control = self.get_control_view(wc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

        # After unlock, you can check-in and cancel again.
        ILockable(wc).unlock()
        control = self.get_control_view(wc)
        self.assertTrue(control.checkin_allowed())
        self.assertTrue(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

    def test_control_cancel_on_original_does_not_delete_original(self):
        # checkout document
        doc = self.portal.docs.doc1
        policy = ICheckinCheckoutPolicy(self.portal.docs.doc1, None)
        policy.checkout(self.portal.workarea)

        # get cancel browser view
        from plone.app.iterate.browser.cancel import Cancel

        cancel = Cancel(doc, self.layer["request"])
        self.layer["request"].form["form.button.Cancel"] = True

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
        rels = list(catalog.findRelations({"from_id": obj_id}))
        self.assertEqual(len(rels), 0)

        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        wc_id = intids.getId(wc)

        rels = list(catalog.findRelations({"from_id": obj_id}))
        self.assertEqual(len(rels), 1)
        from_rel = rels[0]

        rels = list(catalog.findRelations({"to_id": wc_id}))
        self.assertEqual(len(rels), 1)
        to_rel = rels[0]

        self.assertEqual(from_rel, to_rel)

        doc = ICheckinCheckoutPolicy(wc).checkin("updated")

        rels = list(catalog.findRelations({"from_id": obj_id}))

        self.assertEqual(len(rels), 0)

    def test_relationship_deleted_on_cancel_checkout(self):
        # Ensure that the relationship between the baseline and the wc is
        # removed when the working copy is checked in
        folder = self.portal.docs
        doc = folder.doc1

        intids = component.getUtility(IIntIds)
        catalog = component.getUtility(ICatalog)
        obj_id = intids.getId(doc)
        rels = list(catalog.findRelations({"from_id": obj_id}))
        self.assertEqual(len(rels), 0)

        wc = ICheckinCheckoutPolicy(doc).checkout(folder)
        wc_id = intids.getId(wc)

        rels = list(catalog.findRelations({"from_id": obj_id}))
        self.assertEqual(len(rels), 1)
        from_rel = rels[0]

        rels = list(catalog.findRelations({"to_id": wc_id}))
        self.assertEqual(len(rels), 1)
        to_rel = rels[0]

        self.assertEqual(from_rel, to_rel)

        ICheckinCheckoutPolicy(wc).cancelCheckout()

        rels = list(catalog.findRelations({"from_id": obj_id}))

        self.assertEqual(len(rels), 0)

    def test_baseline_relations_updated_on_checkin(self):
        # Ensure that relations between the baseline and
        # and other objects are up-to-date on checkin
        from z3c.relationfield import RelationValue
        from zope.event import notify
        from zope.lifecycleevent import ObjectModifiedEvent

        folder = self.portal.docs
        baseline = folder.doc1
        target = folder.doc2

        intids = component.getUtility(IIntIds)
        catalog = component.getUtility(ICatalog)

        target_id = intids.getId(target)
        target_rel = [RelationValue(target_id)]

        # Test, if nothing is present in the relation catalog
        rels = list(catalog.findRelations({"to_id": target_id}))
        self.assertEqual(len(rels), 0)

        # set relatedItems on baseline
        baseline.relatedItems = target_rel
        notify(ObjectModifiedEvent(baseline))

        # Test, if relation is present in the relation catalog
        rels = list(catalog.findRelations({"to_id": target_id}))
        self.assertEqual(len(rels), 1)

        # make a workingcopy from baseline
        wc = ICheckinCheckoutPolicy(baseline).checkout(folder)

        # remove relations on wc
        wc.relatedItems = []
        notify(ObjectModifiedEvent(wc))

        # baseline -> target relation should be still there, we are on wc
        rels = list(catalog.findRelations({"to_id": target_id}))
        self.assertEqual(len(rels), 1)

        # baseline -> target relation should be empty now
        # because we replaced our baseline with our wc (with empty relations)
        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")
        rels = list(catalog.findRelations({"to_id": target_id}))

        # new baseline's relatedItems should be empty
        self.assertEqual(len(rels), 0)

    def test_publication_behavior_values_not_changed(self):
        doc = self.portal.docs.doc1
        original_effective_date = doc.effective_date
        original_expiration_date = doc.expiration_date
        # Create a working copy
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        # Check in without modifying the existing values
        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")
        # Values should be the same of the original document
        self.assertEqual(original_effective_date, baseline.effective_date)
        self.assertEqual(original_expiration_date, baseline.expiration_date)

    def test_publication_behavior_values_not_changed_value_is_already_set(self):
        doc = self.portal.docs.doc2
        effective_date = DateTime("2021/09/08 10:06:00 UTC")
        doc.effective_date = effective_date
        original_expiration_date = doc.expiration_date
        # Create a working copy
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        # Check in without modifying the existing values
        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")
        # Values should be the same of the original document
        self.assertEqual(effective_date, baseline.effective_date)
        self.assertEqual(original_expiration_date, baseline.expiration_date)

    def test_is_working_copy_in_catalog_metadata(self):
        # Create a working copy
        doc = self.portal.docs.doc1
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)

        # Check catalog metadata
        catalog = self.portal.portal_catalog
        brain = catalog.unrestrictedSearchResults(UID=wc.UID())[0]
        self.assertTrue(brain.is_working_copy)
