from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.iterate import interfaces
from plone.app.iterate.base import BaseContentCopier
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.dexterity.relation import StagingRelationValue
from plone.app.iterate.event import AfterCheckinEvent
from plone.app.relationfield.event import update_behavior_relations
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from z3c.relationfield import event
from z3c.relationfield import RelationValue
from z3c.relationfield.event import updateRelations
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zc.relation.interfaces import ICatalog
from ZODB.PersistentMapping import PersistentMapping
from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder


class ContentCopier(BaseContentCopier):
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
                if field.__name__ == "id":
                    continue
                try:
                    value = field.get(schema(self.context))
                except Exception:
                    value = None

                if name == "effective":
                    baseline.effective_date = self.context.effective_date
                elif name == "expires":
                    baseline.expiration_date = self.context.expiration_date
                elif name == "subjects":
                    baseline.setSubject(self.context.Subject())
                else:
                    field.set(baseline, value)

        baseline.reindexObject()

        # copy annotations
        wc_annotations = IAnnotations(self.context)
        baseline_annotations = IAnnotations(baseline)

        # The next one is just wrong
        # baseline_annotations.clear()

        # Remove plone.folder.ordered.order from it to not mess with the original
        if "plone.folder.ordered.order" in wc_annotations:
            wc_annotations.pop("plone.folder.ordered.order")

        baseline_annotations.update(wc_annotations)

        # delete the working copy
        wc_container._delObject(wc_id)

        return baseline

    def _reassembleWorkingCopy(self, new_baseline, baseline):
        # Does not change Plone Site permissions.
        if new_baseline.portal_type == "Plone Site":
            return new_baseline

        # reattach the source's workflow history, try avoid a dangling ref
        try:
            new_baseline.workflow_history = PersistentMapping(
                baseline.workflow_history.items()
            )
        except AttributeError:
            # No workflow apparently.  Oh well.
            pass

        # reset wf state security directly
        workflow_tool = getToolByName(self.context, "portal_workflow")
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
        catalog = component.queryUtility(ICatalog)
        catalog.unindex(relation)
        return

    def _get_relation_to_baseline(self):
        context = aq_inner(self.context)
        # get id
        intids = component.getUtility(IIntIds)
        id = intids.getId(context)
        # ask catalog
        catalog = component.getUtility(ICatalog)
        relations = catalog.findRelations({"to_id": id})
        relations = [i for i in relations if i.from_attribute == ITERATE_RELATION_NAME]
        # do we have a baseline in our relations?
        if relations and not len(relations) == 1:
            raise interfaces.CheckinException("Baseline count mismatch")

        if not relations or not relations[0]:
            raise interfaces.CheckinException("Baseline has disappeared")
        return relations[0]

    def _getBaseline(self):
        intids = component.getUtility(IIntIds)
        relation = self._get_relation_to_baseline()
        if relation:
            baseline = intids.getObject(relation.from_id)

        if not baseline:
            raise interfaces.CheckinException("Baseline has disappeared")
        return baseline

    def checkin(self, checkin_message):
        # get the baseline for this working copy, raise if not found
        baseline = self._getBaseline()
        # get a hold of the relation object
        relation = self._get_relation_to_baseline()
        # publish the event for subscribers, early because contexts are about
        # to be manipulated
        notify(event.CheckinEvent(self.context, baseline, relation, checkin_message))
        # merge the object back to the baseline with a copier
        copier = component.queryAdapter(self.context, interfaces.IObjectCopier)
        new_baseline = copier.merge()
        # don't need to unlock the lock disappears with old baseline deletion
        notify(AfterCheckinEvent(new_baseline, checkin_message))
        return new_baseline


class FolderishContentCopier(ContentCopier):
    def _copyBaseline(self, container):
        if self.context.portal_type == "Plone Site":
            portal_type = "Document"
        else:
            portal_type = self.context.portal_type
        obj = createContentInContainer(
            container,
            portal_type,
            id=f"working_copy_of_{self.context.id}",
        )
        # Since the working copy of the Portal is originally a Document,
        # we force its portal_type to "Plone Site", so that the "Plone Site"
        # schema is used.
        if self.context.portal_type == "Plone Site":
            obj.portal_type = "Plone Site"
            # Especially in Classic UI we may get a 404 NotFound on the document
            # because it gets its layout/display from the Plone Site FTI.
            document_fti = getUtility(IDexterityFTI, name="Document")
            if obj.getLayout() not in document_fti.view_methods:
                obj._setProperty("layout", document_fti.default_view or "view")

        # copy all field values from the baseline to the working copy
        for schema in iterSchemata(self.context):
            for name, field in getFieldsInOrder(schema):
                # Skip read-only fields
                if field.readonly:
                    continue
                if field.__name__ == "id":
                    continue
                try:
                    value = field.get(schema(self.context))
                except Exception:
                    value = None

                if name == "effective":
                    obj.effective_date = self.context.effective_date
                elif name == "expires":
                    obj.expiration_date = self.context.expiration_date
                elif name == "subjects":
                    obj.setSubject(self.context.Subject())
                elif isinstance(field, RelationList):
                    if value:
                        field.set(
                            obj,
                            [RelationValue(i.to_id) for i in value if not i.isBroken()],
                        )
                elif isinstance(field, RelationChoice):
                    if value and not value.isBroken():
                        field.set(obj, RelationValue(value.to_id))
                else:
                    field.set(obj, value)

        update_relation_catalog(obj)
        obj.reindexObject()

        # copy annotations
        wc_annotations = IAnnotations(obj)
        baseline_annotations = IAnnotations(self.context)

        wc_annotations.update(baseline_annotations)
        # Remove plone.folder.order from it to not spoil the wc
        if "plone.folder.ordered.order" in wc_annotations:
            wc_annotations.pop("plone.folder.ordered.order")
        if "plone.folder.ordered.pos" in wc_annotations:
            wc_annotations.pop("plone.folder.ordered.pos")

        return obj

    def _replaceBaseline(self, baseline):
        wc_id = self.context.getId()
        wc_container = aq_parent(self.context)

        # copy all field values from the working copy to the baseline
        for schema in iterSchemata(baseline):
            for name, field in getFieldsInOrder(schema):
                # Skip read-only fields
                if field.readonly:
                    continue
                if field.__name__ == "id":
                    continue
                try:
                    value = field.get(schema(self.context))
                except Exception:
                    value = None

                if name == "effective":
                    baseline.effective_date = self.context.effective_date
                elif name == "expires":
                    baseline.expiration_date = self.context.expiration_date
                elif name == "subjects":
                    baseline.setSubject(self.context.Subject())
                elif isinstance(field, RelationList):
                    if value:
                        field.set(
                            baseline,
                            [RelationValue(i.to_id) for i in value if not i.isBroken()],
                        )
                elif isinstance(field, RelationChoice):
                    if value and not value.isBroken():
                        field.set(baseline, RelationValue(value.to_id))
                else:
                    field.set(baseline, value)
        update_relation_catalog(baseline)
        baseline.reindexObject()

        # Move working children (newly created objects)
        working_copy_children = [a for a in self.context.objectIds()]

        clipboard = self.context.manage_cutObjects(working_copy_children)
        baseline.manage_pasteObjects(clipboard)

        # copy back annotations
        wc_annotations = IAnnotations(self.context)
        baseline_annotations = IAnnotations(baseline)

        # Remove plone.folder.ordered.order from it to not mess with the original
        if "plone.folder.ordered.order" in wc_annotations:
            wc_annotations.pop("plone.folder.ordered.order")
        if "plone.folder.ordered.pos" in wc_annotations:
            wc_annotations.pop("plone.folder.ordered.pos")

        baseline_annotations.update(wc_annotations)

        # delete the working copy
        wc_container._delObject(wc_id)

        return baseline


def update_relation_catalog(obj):
    # updateRelations from z3c.relationfield does not properly update relations in behaviors
    # that are registered with a marker-interface.
    # update_behavior_relations from plone.app.relationfield does that but does not update
    # those in the main schema.
    updateRelations(obj, None)
    update_behavior_relations(obj, None)
