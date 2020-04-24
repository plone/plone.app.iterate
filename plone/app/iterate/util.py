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

import contextlib

from persistent.dict import PersistentDict

from zope.annotation import IAnnotations
from zope import globalrequest

from AccessControl import SpecialUsers
from AccessControl import SecurityManagement

from Products.CMFPlone.utils import get_installer

from .interfaces import annotation_key


def get_storage(context, default=None):
    annotations = IAnnotations(context)
    if annotation_key not in annotations:
        if default is not None:
            return default
        annotations[annotation_key] = PersistentDict()
    return annotations[annotation_key]


def upgrade_by_reinstall(context):
    qi = get_installer(context)
    qi.uninstall_product('plone.app.iterate')
    qi.install_product('plone.app.iterate')


@contextlib.contextmanager
def adopt_system(user=SpecialUsers.system):
    """
    Execute this block of code as the system user.
    """
    old_security_manager = SecurityManagement.getSecurityManager()
    SecurityManagement.newSecurityManager(globalrequest.getRequest(), user)

    yield

    SecurityManagement.setSecurityManager(old_security_manager)
