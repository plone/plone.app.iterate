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
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.iterate import PloneMessageFactory as _
from plone.app.iterate.interfaces import IWCContainerLocator
from Products.CMFCore.interfaces import IDynamicType
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.interface import implementer


@implementer(IWCContainerLocator)
@adapter(IDynamicType)
class HomeFolderLocator(object):
    """Locate the current user's home folder, if possible.
    """

    def __init__(self, context):
        self.context = context

    title = _(u'Home folder')

    @property
    def available(self):
        return self() is not None

    def __call__(self):
        return getToolByName(self.context, 'portal_membership').getHomeFolder()


@implementer(IWCContainerLocator)
@adapter(IDynamicType)
class ParentFolderLocator(object):
    """Locate the parent of the context, if the user has the
    Add portal content permission.
    """

    def __init__(self, context):
        self.context = context

    title = _(u'Parent folder')

    @property
    def available(self):
        return bool(
            getSecurityManager().checkPermission(
                AddPortalContent,
                aq_parent(aq_inner(self.context))
            )
        )

    def __call__(self):
        if not self.available:
            return None
        return aq_parent(aq_inner(self.context))
