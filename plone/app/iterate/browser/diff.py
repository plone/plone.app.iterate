"""
$Id: diff.py 1807 2007-02-06 06:52:46Z hazmat $
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from plone.app.iterate.interfaces import IWorkingCopy, IBaseline
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy


class DiffView(BrowserView):

    def __call__(self):
        policy = ICheckinCheckoutPolicy(self.context)
        if IBaseline.providedBy(self.context):
            self.baseline = self.context
            self.working_copy = policy.getWorkingCopy()
        elif IWorkingCopy.providedBy(self.context):
            self.working_copy = self.context
            self.baseline = policy.getBaseline()
        else:
            raise AttributeError("Invalid Context")
        return self.index()

    def diffs(self):
        diff = getToolByName(self.context, 'portal_diff')
        return diff.createChangeSet(self.baseline,
                                    self.working_copy,
                                    id1="Baseline",
                                    id2="Working Copy")
