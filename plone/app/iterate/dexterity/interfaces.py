from plone.app.iterate.interfaces import IIterateAware
from zope.interface import Attribute
from z3c.relationfield.interfaces import IRelationValue


class IStagingRelationValue(IRelationValue):
    pass

class IDexterityIterateAware(IIterateAware):
    pass