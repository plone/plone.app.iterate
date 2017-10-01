# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.interfaces import IObjectManager
from plone.app.iterate.base import BaseContentCopier
from plone.app.iterate import interfaces
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.dexterity.relation import StagingRelationValue
from plone.app.iterate.event import AfterCheckinEvent
from plone.app.iterate.interfaces import IBaseline
from plone.dexterity.utils import iterSchemata
from plone.folder.default import DefaultOrdering
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from z3c.relationfield import event
from zc.relation.interfaces import ICatalog
from ZODB.PersistentMapping import PersistentMapping
from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder


WCOPY_ANNOTATION_READONLY = [DefaultOrdering.ORDER_KEY, DefaultOrdering.POS_KEY]


class ContentCopier(BaseContentCopier):

    def clear_annotations(self, ann):
        """  Annotations.clear() doesn't work properly. Some elements remain in the list """
        keys = list(ann.keys())
        for k in keys:
            del ann[k]

    def copyTo(self, container):
        context = aq_inner(self.context)
        wc = self._copyBaseline(container)
        # get id of objects
        intids = component.getUtility(IIntIds)
        wc_id = intids.getId(wc)
        # create a relation
        relation = StagingRelationValue(wc_id)
        event._setRelation(context, ITERATE_RELATION_NAME, relation)
        return wc, relation

    def merge(self):
        baseline = self._getBaseline()

        # delete the working copy reference to the baseline
        self._deleteWorkingCopyRelation()
        # move the working copy to the baseline container, deleting the
        # baseline
        new_baseline = self._replaceBaseline(baseline)

        # patch the working copy with baseline info not preserved during
        # checkout
        self._reassembleWorkingCopy(new_baseline, baseline)

        return new_baseline

    def _replaceBaseline(self, baseline):
        """ Copy all field values and annotations from working-copy to baseline and delete it """
        wc_id = self.context.getId()
        wc_container = aq_parent(self.context)
        self._copy_attributes(self.context, baseline)
        # delete the working copy
        wc_container._delObject(wc_id)
        return baseline

    def _copy_attributes(self, obj_orig, obj_dest, blacklist_annotations=WCOPY_ANNOTATION_READONLY):
        """ Copy all field values and annotations from the obj_orig copy to obj_dest """

        for schema in iterSchemata(obj_dest):
            for name, field in getFieldsInOrder(schema):
                # Skip read-only fields
                if field.readonly:
                    continue
                if field.__name__ == 'id':
                    continue
                try:
                    value = field.get(schema(obj_orig))
                except Exception:
                    value = None

                # TODO: We need a way to identify the DCFieldProperty
                # fields and use the appropriate set_name/get_name
                if name == 'effective':
                    obj_dest.effective_date = obj_orig.effective()
                elif name == 'expires':
                    obj_dest.expiration_date = obj_orig.expires()
                elif name == 'subjects':
                    obj_dest.setSubject(obj_orig.Subject())
                else:
                    field.set(obj_dest, value)

        # copy annotations
        orig_annotations = IAnnotations(obj_orig)
        obj_dest_annotations = IAnnotations(obj_dest)

        # remove the items that are not in wc anymore
        for item in obj_dest_annotations:
            if item not in blacklist_annotations and item not in orig_annotations:
                del obj_dest_annotations[item]

        # Copy all other values from wc
        for item in orig_annotations:
            if item not in blacklist_annotations:
                obj_dest_annotations[item] = orig_annotations[item]
        obj_dest.reindexObject()

    def _reassembleWorkingCopy(self, new_baseline, baseline):
        # reattach the source's workflow history, try avoid a dangling ref
        try:
            new_baseline.workflow_history = PersistentMapping(
                baseline.workflow_history.items())
        except AttributeError:
            # No workflow apparently.  Oh well.
            pass

        # reset wf state security directly
        workflow_tool = getToolByName(self.context, 'portal_workflow')
        wfs = workflow_tool.getWorkflowsFor(self.context)
        for wf in wfs:
            if not isinstance(wf, DCWorkflowDefinition):
                continue
            wf.updateRoleMappingsFor(new_baseline)
        return new_baseline

    def _handleReferences(self, baseline, wc, mode, wc_ref):
        pass

    def _deleteWorkingCopyRelation(self):
        # delete the wc reference keeping a reference to it for its annotations
        relation = self._get_relation_to_baseline()
        relation.broken(relation.to_path)
        return relation

    def _get_relation_to_baseline(self):
        context = aq_inner(self.context)
        # get id
        intids = component.getUtility(IIntIds)
        id = intids.getId(context)
        # ask catalog
        catalog = component.getUtility(ICatalog)
        relations = list(catalog.findRelations({'to_id': id}))
        relations = filter(lambda r: r.from_attribute == ITERATE_RELATION_NAME,
                           relations)

        if not relations or relations[0] is None:
            raise interfaces.CheckinException('Working copy has no reference to the original object (baseline)')
        elif len(relations) > 1:
            raise interfaces.CheckinException('Working copy has too many references to origin')
        return relations[0]

    def _getBaseline(self):
        intids = component.getUtility(IIntIds)
        relation = self._get_relation_to_baseline()
        if relation:
            baseline = intids.getObject(relation.from_id)

        if not baseline:
            raise interfaces.CheckinException('Working copy has no reference to the original object (baseline)')
        return baseline

    def checkin(self, checkin_message):
        # get the baseline for this working copy, raise if not found
        baseline = self._getBaseline()
        # get a hold of the relation object
        relation = self._get_relation_to_baseline()
        # publish the event for subscribers, early because contexts are about
        # to be manipulated
        notify(event.CheckinEvent(self.context,
                                  baseline,
                                  relation,
                                  checkin_message
                                  ))
        # merge the object back to the baseline with a copier
        copier = component.queryAdapter(self.context,
                                        interfaces.IObjectCopier)
        new_baseline = copier.merge()
        # don't need to unlock the lock disappears with old baseline deletion
        notify(AfterCheckinEvent(new_baseline, checkin_message))
        return new_baseline

    def _copyBaseline(self, container):
        # copy the context from source to the target container
        target_id = container.invokeFactory(self.context.portal_type, id=container._get_id(self.context.getId()))
        target = container._getOb(target_id)
        self._copy_attributes(self.context, target)
        return target


class ContainerCopier(ContentCopier):
    def _copyBaseline(self, container):
        alsoProvides(self.context, IBaseline)
        return super(ContainerCopier, self)._copyBaseline(container)


def object_copied(ob, event):
    if IObjectManager.providedBy(ob):
        # Remove all references to children
        ids = list(ob.objectIds())
        for i in ids:
             ob._delOb(i)
        ann = IAnnotations(ob)
        del ann[DefaultOrdering.ORDER_KEY]
        del ann[DefaultOrdering.POS_KEY]
