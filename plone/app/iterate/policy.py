# -*- coding: utf-8 -*-
##################################################################
#
# (C) Copyright 2006-2007 ObjectRealms, LLC
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
Archetypes Checkin Checkout Policy For Content

"""
from plone.app.iterate.base import CheckinCheckoutBasePolicyAdapter
from plone.app.iterate.event import AfterCheckinEvent
from plone.app.iterate.event import CheckinEvent
from plone.app.iterate.interfaces import CheckinException
from plone.app.iterate.interfaces import IIterateAware
from plone.app.iterate.interfaces import IObjectCopier
from plone.app.iterate.relation import WorkingCopyRelation
from plone.app.iterate.util import get_storage
from Products.Archetypes.interfaces import IReferenceable
from zope.component import adapter
from zope.component import queryAdapter
from zope.event import notify


@adapter(IIterateAware)
class CheckinCheckoutPolicyAdapter(CheckinCheckoutBasePolicyAdapter):
    """Checkin Checkout Policy For Archetypes Content

    - on checkout context is the baseline
    - on checkin context is the working copy.
    """

    def checkin(self, checkin_message):
        # see interface

        # get the baseline for this working copy, raise if not found
        baseline = self._getBaseline()

        # get a hold of the relation object
        wc_ref = self.context.getReferenceImpl(
            WorkingCopyRelation.relationship
        )[0]

        # publish the event for subscribers, early because contexts are about
        # to be manipulated
        notify(CheckinEvent(self.context, baseline, wc_ref, checkin_message))

        # merge the object back to the baseline with a copier

        # XXX by gotcha
        # bug we should or use a getAdapter call or test if copier is None
        copier = queryAdapter(self.context, IObjectCopier)
        new_baseline = copier.merge()

        # don't need to unlock the lock disappears with old baseline deletion
        notify(AfterCheckinEvent(new_baseline, checkin_message))

        return new_baseline

    #################################
    #  Checkin Support Methods

    def _getBaseline(self):
        # follow the working copy's reference back to the baseline
        refs = self.context.getReferences(WorkingCopyRelation.relationship)

        if not len(refs) == 1:
            raise CheckinException('Baseline count mismatch')

        if not refs or refs[0] is None:
            raise CheckinException('Baseline has disappeared')

        baseline = refs[0]
        return baseline

    def getBaseline(self):
        if IReferenceable.providedBy(self.context):
            refs = self.context.getReferences(WorkingCopyRelation.relationship)
            if refs:
                return refs[0]

    def getWorkingCopy(self):
        if IReferenceable.providedBy(self.context):
            refs = self.context.getBRefs(WorkingCopyRelation.relationship)
            if refs:
                return refs[0]

    def getProperties(self, obj, default=None):
        return get_storage(obj, default=default)
