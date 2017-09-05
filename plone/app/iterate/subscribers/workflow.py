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
$Id: workflow.py 1824 2007-02-08 17:59:41Z hazmat $

Applies new checkout specific workflows to content that is checked out.

"""

from Acquisition import aq_base
from plone.app.iterate.interfaces import IIterateSettings
from plone.app.iterate.util import get_storage
from plone.registry.interfaces import IRegistry
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id  # noqa
from Products.CMFPlacefulWorkflow.WorkflowPolicyConfig import WorkflowPolicyConfig  # noqa
from zope.component import getUtility


USE_WORKFLOW = 'checkout_workflow_policy'

policy_storage = 'previous_wf_policy'


def handleCheckout(event):
    # defer to setting
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IIterateSettings)
    if not settings.enable_checkout_workflow:
        return
    policy_id = settings.checkout_workflow_policy

    existing_policy = getattr(
        aq_base(event.working_copy), WorkflowPolicyConfig_id, None)
    storage = get_storage(event.relation)

    # set config for policy in and below
    policy = WorkflowPolicyConfig(policy_id, policy_id)
    policy.coci_created = True

    if existing_policy is not None:
        storage[policy_storage] = policy

    # we setattr because we want the effect on non containerish objects
    setattr(event.working_copy, WorkflowPolicyConfig_id, policy)
    event.working_copy.notifyWorkflowCreated()
    event.working_copy.reindexObjectSecurity()


def handleCheckin(event):
    policy = getattr(aq_base(event.object), WorkflowPolicyConfig_id, None)
    storage = get_storage(event.relation)
    previous_policy = storage.get(policy_storage)
    if previous_policy is None:
        # only reset workflows we know.. could use are own storage
        if policy and not getattr(policy, 'coci_created', False):
            return
        elif policy is None:
            return
        else:
            delattr(event.object, WorkflowPolicyConfig_id)
    else:
        setattr(event.object, WorkflowPolicyConfig_id, previous_policy)
