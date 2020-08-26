# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import warnings


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            u'plone.app.iterate:uninstall',
            u'plone.app.iterate:plone.app.iterate',
        ]


def deprecate_profile(tool):
    """Deprecation profile plone.app.iterate.

    Deprecation warning for plone.app.iterate:plone.app.iterate profile.
    """
    warnings.warn(
        'The profile with id "plone.app.iterate" was renamed to "default".',
        DeprecationWarning
    )
