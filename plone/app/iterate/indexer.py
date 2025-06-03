from plone.indexer import indexer
from plone.app.iterate.interfaces import IWorkingCopy


@indexer(IWorkingCopy)
def is_working_copy(obj):
    return True
