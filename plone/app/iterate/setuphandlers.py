# -*- coding: utf-8 -*-
"""Deprecation warning for plone.app.iterate:plone.app.iterate profile."""

import warnings


def deprecate_profile(tool):
    """Deprecation profile plone.app.iterate."""
    warnings.warn(
        'The profile with id "plone.app.iterate" was renamed to "default".',
        DeprecationWarning
    )
