# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from zc.relation.interfaces import ICatalog
from zope import component
from zope.intid.interfaces import IIntIds


def get_relations(context):
    context = aq_inner(context)
    # get id
    intids = component.getUtility(IIntIds)
    id = intids.queryId(aq_base(context))
    if not id:
        # for objects without intid or
        # objects being deleted in the current transaction return empty list
        return []
    # ask catalog
    catalog = component.getUtility(ICatalog)
    relations = list(catalog.findRelations({'to_id': id}))
    relations += list(catalog.findRelations({'from_id': id}))
    relations = filter(lambda r: r.from_attribute ==
                       ITERATE_RELATION_NAME, relations)
    return relations


def get_checkout_relation(context):
    relations = get_relations(context)
    if len(relations) > 0:
        return relations[0]
    else:
        return None


def get_baseline(context):
    relation = get_checkout_relation(context)
    if relation and relation.from_id:
        intids = component.getUtility(IIntIds)
        return intids.getObject(relation.from_id)
    return None


def get_working_copy(context):
    relation = get_checkout_relation(context)
    if relation and relation.to_id:
        intids = component.getUtility(IIntIds)
        return intids.getObject(relation.to_id)
    return None
