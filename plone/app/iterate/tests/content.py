# -*- coding: utf-8 -*-
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import registerATCT


RichFolderSchema = ATFolderSchema.copy() + atapi.Schema((
    atapi.TextField('text',
                    default_output_type='text/x-html-safe',
                    widget=atapi.RichWidget(),
                    ),
))


class RichFolder(ATFolder):
    """ sample content type for testing purposes """

    schema = RichFolderSchema
    portal_type = 'RichFolder'


registerATCT(RichFolder, 'plone.app.iterate')


def addRichFolder(container, id, **kwargs):
    """ at-constructor copied from ClassGen.py """
    obj = RichFolder(id)
    container._setObject(id, obj, suppress_events=True)
    obj = container._getOb(id)
    obj.manage_afterAdd(obj, container)
    obj.initializeArchetype(**kwargs)
    return obj.getId()
