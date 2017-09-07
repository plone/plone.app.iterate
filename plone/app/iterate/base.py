# -*- coding: utf-8 -*-
##################################################################
#
# (C) Copyright 2006-2007 ObjectRealms, LLC
# (C) Copyright 2007-2017 Plone Foundation
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
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
Base Checkin Checkout Policy For Content

"""

from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.iterate import interfaces
from plone.app.iterate.event import BeforeCheckoutEvent
from plone.app.iterate.event import CancelCheckoutEvent
from plone.app.iterate.event import CheckoutEvent
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IObjectCopier
from plone.app.iterate.util import get_storage
from Products.CMFCore import interfaces as cmf_ifaces
from Products.CMFCore.utils import getToolByName
from zope import component
from zope.component import queryAdapter
from zope.event import notify
from zope.interface import implementer


@implementer(ICheckinCheckoutPolicy)
class CheckinCheckoutBasePolicyAdapter(object):
    """Base Checkin Checkout Policy For Content

    - on checkout context is the baseline
    - on checkin context is the working copy.

    """

    # used when creating baseline version for first time
    default_base_message = 'Created Baseline'

    def __init__(self, context):
        self.context = context

    def checkin(self, checkin_message):
        raise NotImplemented()

    def checkout(self, container):
        # see interface
        notify(BeforeCheckoutEvent(self.context))

        # use the object copier to checkout the content to the container
        copier = queryAdapter(self.context, IObjectCopier)
        working_copy, relation = copier.copyTo(container)

        # publish the event for any subscribers
        notify(CheckoutEvent(self.context, working_copy, relation))

        # finally return the working copy
        return working_copy

    def cancelCheckout(self):
        # see interface

        # get the baseline
        baseline = self._getBaseline()

        # publish an event
        notify(CancelCheckoutEvent(self.context, baseline))

        # delete the working copy
        wc_container = aq_parent(aq_inner(self.context))
        wc_container.manage_delObjects([self.context.getId()])

        return baseline

    #################################
    #  Checkin Support Methods

    def getBaseline(self):
        raise NotImplemented()

    def getWorkingCopy(self):
        raise NotImplemented()

    def getProperties(self, obj, default=None):
        return get_storage(obj, default=default)


@implementer(interfaces.IObjectCopier)
@component.adapter(interfaces.IIterateAware)
class BaseContentCopier(object):

    def __init__(self, context):
        self.context = context

    def _recursivelyReattachUIDs(self, baseline, new_baseline):
        original_refs = len(new_baseline.getRefs())
        original_back_refs = len(new_baseline.getBRefs())
        new_baseline._setUID(baseline.UID())
        new_refs = len(new_baseline.getRefs())
        new_back_refs = len(new_baseline.getBRefs())
        if original_refs != new_refs:
            self._removeDuplicateReferences(new_baseline, backrefs=False)
        if original_back_refs != new_back_refs:
            self._removeDuplicateReferences(new_baseline, backrefs=True)

        if cmf_ifaces.IFolderish.providedBy(baseline):
            new_ids = new_baseline.contentIds()
            for child in baseline.contentValues():
                if child.getId() in new_ids:
                    self._recursivelyReattachUIDs(
                        child, new_baseline[child.getId()])

    def _removeDuplicateReferences(self, item, backrefs=False):
        # Remove duplicate (back) references from this item.
        reference_tool = getToolByName(self.context, 'reference_catalog')
        if backrefs:
            ref_func = reference_tool.getBackReferences
        else:
            ref_func = reference_tool.getReferences
        try:
            # Plone 4.1 or later
            brains = ref_func(item, objects=False)
        except TypeError:
            # Plone 4.0 or earlier.  Nothing to fix here
            return
        for brain in brains:
            if brain.getObject() is None:
                reference_tool.uncatalog_object(brain.getPath())

    #################################
    # Checkout Support Methods

    def _copyBaseline(self, container):
        # copy the context from source to the target container
        source_container = aq_parent(aq_inner(self.context))
        clipboard = source_container.manage_copyObjects([self.context.getId()])
        result = container.manage_pasteObjects(clipboard)

        # get a reference to the working copy
        target_id = result[0]['new_id']
        target = container._getOb(target_id)
        return target