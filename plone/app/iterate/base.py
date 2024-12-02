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
from zc.relation.interfaces import ICatalog
from zope import component
from zope.component import queryAdapter
from zope.event import notify
from zope.interface import implementer


@implementer(ICheckinCheckoutPolicy)
class CheckinCheckoutBasePolicyAdapter:
    """Base Checkin Checkout Policy For Content

    - on checkout context is the baseline
    - on checkin context is the working copy.

    """

    # used when creating baseline version for first time
    default_base_message = "Created Baseline"

    def __init__(self, context):
        self.context = context

    def checkin(self, checkin_message):
        raise NotImplementedError()

    def checkout(self, container):
        # see interface
        notify(BeforeCheckoutEvent(self.context))

        # use the object copier to checkout the content to the container
        copier = queryAdapter(self.context, IObjectCopier)
        # The container for the Portal's working copy is the Portal itself.
        if self.context.portal_type == "Plone Site":
            working_copy_container = self.context
        else:
            working_copy_container = container
        working_copy, relation = copier.copyTo(working_copy_container)

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

        # Remove the relationship
        relation = self._get_relation_to_baseline()
        catalog = component.queryUtility(ICatalog)
        catalog.unindex(relation)

        # delete the working copy
        wc_container = aq_parent(aq_inner(self.context))
        wc_container.manage_delObjects([self.context.getId()])

        return baseline

    #################################
    #  Checkin Support Methods

    def getBaseline(self):
        raise NotImplementedError()

    def getWorkingCopy(self):
        raise NotImplementedError()

    def getProperties(self, obj, default=None):
        return get_storage(obj, default=default)


@implementer(interfaces.IObjectCopier)
@component.adapter(interfaces.IIterateAware)
class BaseContentCopier:
    def __init__(self, context):
        self.context = context

    def _copyBaseline(self, container):
        # copy the context from source to the target container
        source_container = aq_parent(aq_inner(self.context))
        clipboard = source_container.manage_copyObjects([self.context.getId()])
        result = container.manage_pasteObjects(clipboard)

        # get a reference to the working copy
        target_id = result[0]["new_id"]
        target = container._getOb(target_id)
        return target
