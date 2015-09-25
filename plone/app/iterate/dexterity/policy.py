from plone.app import iterate
from plone.app.iterate.dexterity.utils import get_baseline
from plone.app.iterate.dexterity.utils import get_checkout_relation
from plone.app.iterate.dexterity.utils import get_relations
from plone.app.iterate.dexterity.utils import get_working_copy
from plone.app.iterate.util import get_storage
from zope import component
from zope.event import notify
from zope.interface import implements


class CheckinCheckoutPolicyAdapter(iterate.policy.CheckinCheckoutPolicyAdapter):
    """
    Dexterity Checkin Checkout Policy
    """
    implements(iterate.interfaces.ICheckinCheckoutPolicy)

    def _get_relation_to_baseline(self):
        # do we have a baseline in our relations?
        relations = get_relations(self.context)

        if relations and not len(relations) == 1:
            raise iterate.interfaces.CheckinException("Baseline count mismatch")

        if not relations or not relations[0]:
            raise iterate.interfaces.CheckinException("Baseline has disappeared")

        return relations[0]

    def _getBaseline(self):
        baseline = get_baseline(self.context)
        if not baseline:
            raise iterate.interfaces.CheckinException("Baseline has disappeared")
        return baseline

    def checkin(self, checkin_message):
        # get the baseline for this working copy, raise if not found
        baseline = self._getBaseline()
        # get a hold of the relation object
        relation = self._get_relation_to_baseline()
        # publish the event for subscribers, early because contexts are about to be manipulated
        notify(iterate.event.CheckinEvent(self.context,
                                          baseline,
                                          relation,
                                          checkin_message))
        # merge the object back to the baseline with a copier
        copier = component.queryAdapter(self.context,
                                        iterate.interfaces.IObjectCopier)
        new_baseline = copier.merge()
        # don't need to unlock the lock disappears with old baseline deletion
        notify(iterate.event.AfterCheckinEvent(new_baseline, checkin_message))
        return new_baseline

    def getBaseline(self):
        return get_baseline(self.context)

    def getWorkingCopy(self):
        return get_working_copy(self.context)

    def getProperties(self, obj, default=None):
        try:
            return get_storage(get_checkout_relation(obj), default=default)
        except AttributeError:
            return default