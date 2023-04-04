from plone.app.contenttypes.interfaces import IDocument
from plone.dexterity.content import Container
from zope.interface import implementer
from zope.interface import Interface


class IFolderishDocument(Interface):
    """Marker interface"""


@implementer(IDocument, IFolderishDocument)
class FolderishDocument(Container):
    """A Dexterity based test type containing a set of standard fields."""

    pass
