from plone.app.iterate.interfaces import IWorkingCopy
from plone.indexer import indexer


@indexer(IWorkingCopy)
def is_working_copy(obj):
    return True
