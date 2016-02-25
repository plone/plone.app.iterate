# -*- coding: utf-8 -*-
"""Deprecation warning for plone.app.iterate:plone.app.iterate profile."""

import warnings


def deprecate_profile(context):
    """Deprecation profile plone.app.iterate."""
    if context.readDataFile('ploneappiterate_plone.app.iterate.txt'):
        warnings.warn('Do no use this profile anymore, use the default profile')
