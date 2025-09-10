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
from Acquisition import aq_inner
from plone.app.iterate import interfaces
from plone.app.iterate import lock
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IWorkingCopy
from plone.app.iterate.permissions import CheckinPermission
from plone.app.iterate.permissions import CheckoutPermission
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView

import Products.CMFCore.permissions


class Control(BrowserView):
    """Information about whether iterate can operate.

    This is a public view, referenced in action condition expressions.
    """

    def _can_lock(self):
        try:
            if lock.isLocked(self.context):
                return False
        except TypeError:
            # This portal_type does not support locking.
            return False
        return True

    def checkin_allowed(self):
        """Check if a checkin is allowed"""
        context = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission

        if not interfaces.IIterateAware.providedBy(context):
            return False

        if not IWorkingCopy.providedBy(context):
            return False

        if not self._can_lock():
            return False

        policy = ICheckinCheckoutPolicy(context, None)
        if policy is None:
            return False

        original = policy.getBaseline()
        if original is None:
            return False

        can_modify = checkPermission(
            Products.CMFCore.permissions.ModifyPortalContent,
            original,
        )
        if not can_modify:
            return False

        can_checkin = checkPermission(
            CheckinPermission,
            original,
        )
        if not can_checkin:
            return False

        return True

    def checkout_allowed(self):
        """Check if a checkout is allowed."""
        context = aq_inner(self.context)

        if not interfaces.IIterateAware.providedBy(context):
            return False

        if not self._can_lock():
            return False

        policy = ICheckinCheckoutPolicy(context, None)
        if policy is None:
            return False

        if policy.getWorkingCopy() is not None:
            return False

        # check if its is a checkout
        if policy.getBaseline() is not None:
            return False

        checkPermission = getSecurityManager().checkPermission
        can_checkout = checkPermission(
            CheckoutPermission,
            context,
        )
        if not can_checkout:
            return False

        return True

    @memoize
    def cancel_allowed(self):
        """Check to see if the user can cancel the checkout on the
        given working copy
        """
        if not self._can_lock():
            return False
        policy = ICheckinCheckoutPolicy(self.context, None)
        if policy is None:
            return False
        original = policy.getBaseline()
        return original is not None
