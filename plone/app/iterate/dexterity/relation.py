from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from persistent.dict import PersistentDict
from plone.app.iterate.dexterity.interfaces import IStagingRelationValue
from z3c.relationfield import relation
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from zope.interface import implements


try:
    from zope.intid.interfaces import IIntIds
except ImportError:
    from zope.app.intid.interfaces import IIntIds


class StagingRelationValue(relation.RelationValue):
    implements(IStagingRelationValue, IAttributeAnnotatable)

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
            condition = lambda r: r.from_attribute == from_attribute and not r.is_broken()
            items = filter(condition, items)
        return items

    def __init__(self, to_id):
        super(StagingRelationValue, self).__init__(to_id)
        self.iterate_properties = PersistentDict()
        # remember the creator
        portal = getUtility(ISiteRoot)
        mstool = getToolByName(portal, 'portal_membership')
        self.creator = mstool.getAuthenticatedMember().getId()
