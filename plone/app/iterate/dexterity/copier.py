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


WC_ANNOTATION_READONLY = [DefaultOrdering.ORDER_KEY, DefaultOrdering.POS_KEY]


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
        wc_id = self.context.getId()
        wc_container = aq_parent(self.context)

        # copy all field values from the working copy to the baseline
        for schema in iterSchemata(baseline):
            for name, field in getFieldsInOrder(schema):
                # Skip read-only fields
                if field.readonly:
                    continue
                if field.__name__ == 'id':
                    continue
                try:
                    value = field.get(schema(self.context))
                except Exception:
                    value = None

                # TODO: We need a way to identify the DCFieldProperty
                # fields and use the appropriate set_name/get_name
                if name == 'effective':
                    baseline.effective_date = self.context.effective()
                elif name == 'expires':
                    baseline.expiration_date = self.context.expires()
                elif name == 'subjects':
                    baseline.setSubject(self.context.Subject())
                else:
                    field.set(baseline, value)

        baseline.reindexObject()

        # copy annotations
        wc_annotations = IAnnotations(self.context)
        baseline_annotations = IAnnotations(baseline)

        # remove the items that are not in wc anymore
        for item in baseline_annotations:
            if item not in WC_ANNOTATION_READONLY and item not in wc_annotations:
                del baseline_annotations[item]

        # Copy all other values from wc
        for item in wc_annotations:
            if item not in WC_ANNOTATION_READONLY:
                baseline_annotations[item] = wc_annotations[item]

        self.clear_annotations(wc_annotations)

        # delete the working copy
        wc_container._delObject(wc_id)

        return baseline

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
        # do we have a baseline in our relations?
        if relations and not len(relations) == 1:
            raise interfaces.CheckinException('Baseline count mismatch')

        if not relations or not relations[0]:
            raise interfaces.CheckinException('Baseline has disappeared')
        return relations[0]

    def _getBaseline(self):
        intids = component.getUtility(IIntIds)
        relation = self._get_relation_to_baseline()
        if relation:
            baseline = intids.getObject(relation.from_id)

        if not baseline:
            raise interfaces.CheckinException('Baseline has disappeared')
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
        source_container = aq_parent(aq_inner(self.context))
        clipboard = source_container.manage_copyObjects([self.context.getId()])
        result = container.manage_pasteObjects(clipboard)
        # get a reference to the working copy
        target_id = result[0]['new_id']
        target = container._getOb(target_id)
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
