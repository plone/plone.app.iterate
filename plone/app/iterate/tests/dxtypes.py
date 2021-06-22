# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.app.contenttypes.interfaces import IDocument
from zope.interface import Interface
from zope.interface import implementer


class IFolderishDocument(Interface):
    """Marker interface"""


@implementer(IDocument, IFolderishDocument)
class FolderishDocument(Container):
    """A Dexterity based test type containing a set of standard fields."""

    pass
