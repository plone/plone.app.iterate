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
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import ILockable
from z3c.relationfield import RelationValue
from zc.relation.interfaces import ICatalog
from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.intid.interfaces import IIntIds

import unittest


class TestIterations(unittest.TestCase):
    """Test plone.app.iterate on containers."""

    layer = PLONEAPPITERATEDEX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

        self.wf = self.portal.portal_workflow
        self.wf.setChainForPortalTypes(
            ("FolderishDocument",), "simple_publication_workflow"
        )

        # add a folder with two documents in it
        self.portal.invokeFactory("Folder", "docs")
        self.portal.docs.invokeFactory("FolderishDocument", "doc1")
        self.portal.docs.invokeFactory("FolderishDocument", "doc2")

        # add a working copy folder
        self.portal.invokeFactory("Folder", "workarea")

        self.repo = self.portal.portal_repository

    def get_control_view(self, doc):
        # Remove any memoized items from the request.
        # Especially, we may have memoized 'cancel_allowed'.
        request = self.layer["request"]
        IAnnotations(request).pop("plone.memoize", None)
        return Control(doc, request)

    def test_container_workflowState(self):
        # ensure baseline workflow state is retained on checkin, including
        # security

        doc = self.portal.docs.doc1

        # sanity check that owner can edit visible docs
        setRoles(self.portal, TEST_USER_ID, ["Owner"])
        self.assertTrue(
            getSecurityManager().checkPermission(
                "Modify portal content", self.portal.docs.doc1
            )
        )

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.wf.doActionFor(doc, "publish")
        state = self.wf.getInfoFor(doc, "review_state")

        self.repo.save(doc)
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        wc_state = self.wf.getInfoFor(wc, "review_state")

        self.assertNotEqual(state, wc_state)

        baseline = ICheckinCheckoutPolicy(wc).checkin("modified")
        bstate = self.wf.getInfoFor(baseline, "review_state")
        self.assertEqual(bstate, "published")

        self.assertEqual(len(self.portal.workarea.objectIds()), 0)
        setRoles(self.portal, TEST_USER_ID, ["Owner"])

    def test_container_baselineCreated(self):
        # if a baseline has no version ensure that one is created on checkout
        self.assertIn("FolderishDocument", self.repo.getVersionableContentTypes())

        doc = self.portal.docs.doc1
        self.assertTrue(self.repo.isVersionable(doc))

        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)

        self.assertEqual(wc.id, "working_copy_of_doc1")
        self.assertIn("working_copy_of_doc1", self.portal.workarea.objectIds())

    def test_container_folderOrder(self):
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

    def test_container_contents(self):
        """When an folderish content is checked out, and item is added, and then
        the content is checked back in, if resources (images or files) are added item is in the new
        version of the folder they are moved to the baseline container.  UIDs of contained content are also
        preserved."""
        container = self.portal.docs
        doc = container.doc1

        wc = ICheckinCheckoutPolicy(doc).checkout(container)
        self.repo.save(wc)
        image = createContentInContainer(
            wc,
            "Image",
            id="an-image",
        )
        another_doc = createContentInContainer(
            wc,
            "FolderishDocument",
            id="document",
        )
        just_another_nested_doc = createContentInContainer(
            another_doc,
            "FolderishDocument",
            id="just_another_doc",
        )
        image_uid = image.UID()
        another_doc_uid = another_doc.UID()
        just_another_nested_doc_uid = just_another_nested_doc.UID()

        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")

        self.assertTrue("an-image" in baseline)
        self.assertTrue("document" in baseline)
        self.assertTrue("just_another_doc" in baseline["document"])
        self.assertEqual(baseline["an-image"].UID(), image_uid)
        self.assertEqual(baseline["document"].UID(), another_doc_uid)
        self.assertEqual(
            baseline["document"]["just_another_doc"].UID(), just_another_nested_doc_uid
        )

    def test_container_contents_with_collisions(self):
        """When an folderish content is checked out, and item is added, and then
        the content is checked back in, if resources (images or files) are added item is in the new
        version of the folder they are moved to the baseline container.  UIDs of contained content are also
        preserved and collisions handled by Zope cut/paste machinery."""
        container = self.portal.docs
        baseline = container.doc1
        baseline_image = createContentInContainer(
            baseline,
            "Image",
            id="an-image",
        )
        self.repo.save(baseline)
        baseline_image_uid = baseline_image.UID()

        wc = ICheckinCheckoutPolicy(baseline).checkout(container)
        self.repo.save(wc)
        image = createContentInContainer(
            wc,
            "Image",
            id="an-image",
        )
        image_uid = image.UID()

        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")

        self.assertTrue("copy_of_an-image" in baseline)
        self.assertTrue("an-image" in baseline)
        self.assertEqual(baseline["an-image"].UID(), baseline_image_uid)
        self.assertEqual(baseline["copy_of_an-image"].UID(), image_uid)

    def test_container_default_page_is_kept_in_folder(self):
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

    def test_container_control_portal(self):
        # The portal is not versionable, but it is lockable.
        doc = self.portal
        self.assertNotIn("Plone Site", self.repo.getVersionableContentTypes())
        self.assertFalse(self.repo.isVersionable(doc))
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

    def test_container_control_lockable_folder(self):
        # LockableFolder is not versionable, but it is lockable.
        self.portal.invokeFactory("LockableFolder", "safe")
        doc = self.portal.safe
        self.assertNotIn("LockableFolder", self.repo.getVersionableContentTypes())
        self.assertFalse(self.repo.isVersionable(doc))
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

    def test_container_control_normal_folder(self):
        # Folder is not versionable, and not lockable.
        doc = self.portal.docs
        self.assertNotIn("Folder", self.repo.getVersionableContentTypes())
        self.assertFalse(self.repo.isVersionable(doc))
        try:
            lockable = ILockable(doc)
        except TypeError:
            lockable = False
        self.assertFalse(lockable)

        # Nothing is allowed.
        control = self.get_control_view(doc)
        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

    def test_container_control_folderish_document(self):
        # FolderishDocument is both versionable and lockable.
        doc = self.portal.docs.doc1
        self.assertIn("FolderishDocument", self.repo.getVersionableContentTypes())
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
        IAnnotations(self.layer["request"]).pop("plone.memoize", None)

        self.assertFalse(control.checkin_allowed())
        self.assertFalse(control.cancel_allowed())
        self.assertFalse(control.checkout_allowed())

    def test_container_control_cancel_on_original_does_not_delete_original(self):
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

    def test_container_relationship_deleted_on_checkin(self):
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

    def test_relationfield_handling(self):
        # relations are not simply copied
        folder = self.portal.docs
        doc = folder.doc1
        target = folder.doc2
        intids = component.getUtility(IIntIds)
        doc.relatedItems = [RelationValue(intids.getId(target))]
        wc = ICheckinCheckoutPolicy(doc).checkout(doc)
        self.assertNotEqual(doc.relatedItems[0], wc.relatedItems[0])
        self.assertEqual(doc.relatedItems[0].to_object, target)
        self.assertEqual(doc.relatedItems[0].from_object, doc)
        self.assertEqual(wc.relatedItems[0].to_object, target)
        self.assertEqual(wc.relatedItems[0].from_object, wc)
        wc = ICheckinCheckoutPolicy(wc).checkin("modified")
        self.assertEqual(doc.relatedItems[0].to_object, target)
        self.assertEqual(doc.relatedItems[0].from_object, doc)
        self.assertEqual(len(doc.relatedItems), 1)

        wc = ICheckinCheckoutPolicy(doc).checkout(doc)
        wc.relatedItems = [RelationValue(intids.getId(folder))]
        wc = ICheckinCheckoutPolicy(wc).checkin("modified")
        self.assertEqual(doc.relatedItems[0].to_object, folder)
        self.assertEqual(doc.relatedItems[0].from_object, doc)
        self.assertEqual(len(doc.relatedItems), 1)

    def test_publication_behavior_values_not_changed_folderish(self):
        doc = self.portal.docs.doc2
        original_effective_date = doc.effective_date
        original_expiration_date = doc.expiration_date
        # Create a working copy
        wc = ICheckinCheckoutPolicy(doc).checkout(self.portal.workarea)
        # Check in without modifying the existing values
        baseline = ICheckinCheckoutPolicy(wc).checkin("updated")
        # Values should be the same of the original document
        self.assertEqual(original_effective_date, baseline.effective_date)
        self.assertEqual(original_expiration_date, baseline.expiration_date)
