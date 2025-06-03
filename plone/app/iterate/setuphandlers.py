from plone.base.interfaces.installable import INonInstallable
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            "plone.app.iterate:uninstall",
            "plone.app.iterate:to1000",
        ]


def reindex_working_copies(context):
    logger.info("Reindexing working copies...")
    catalog = getToolByName(context, "portal_catalog")
    for brain in catalog.unrestrictedSearchResults(
        object_provides="plone.app.iterate.interfaces.IWorkingCopy"
    ):
        obj = brain.getObject()
        obj.reindexObject(idxs=["getId"], update_metadata=True)
