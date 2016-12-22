# -*- coding: utf-8 -*-
from plone.app.iterate.dexterity.interfaces import IStagingRelationValue
from z3c.relationfield import relation
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds


@implementer(IStagingRelationValue, IAttributeAnnotatable)
class StagingRelationValue(relation.RelationValue):

    @classmethod
    def get_relations_of(cls, obj, from_attribute=None):
        """ a list of relations to or from the passed object
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        obj_id = intids.getId(obj)
        items = list(catalog.findRelations({'from_id': obj_id}))
        items += list(catalog.findRelations({'to_id': obj_id}))
        if from_attribute:

            def condition(r):
                return r.from_attribute == from_attribute and not r.is_broken()

            items = filter(condition, items)
        return items
