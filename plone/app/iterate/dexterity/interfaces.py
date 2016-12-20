# -*- coding: utf-8 -*-
from plone.app.iterate.interfaces import IIterateAware
from z3c.relationfield.interfaces import IRelationValue


class IStagingRelationValue(IRelationValue):
    pass


class IDexterityIterateAware(IIterateAware):
    pass
