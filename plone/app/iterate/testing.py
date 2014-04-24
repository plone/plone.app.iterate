# -*- coding: utf-8 -*-

from zope.configuration import xmlconfig

from plone.testing import z2

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


class PloneAppIterateLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.iterate')
        import plone.app.iterate
        xmlconfig.file(
            'configure.zcml',
            plone.app.iterate,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.ATContentTypes:default')
        applyProfile(portal, 'plone.app.iterate:plone.app.iterate')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        portal.acl_users.userFolderAddUser('test_editor',
                                           'secret',
                                           ['Editor'],
                                           [])
        portal.acl_users.userFolderAddUser('test_contributor',
                                           'secret',
                                           ['Contributor'],
                                           [])
        portal.portal_workflow.setChainForPortalTypes(('Document',), 'plone_workflow')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.iterate')

PLONEAPPITERATE_FIXTURE = PloneAppIterateLayer()

PLONEAPPITERATE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPITERATE_FIXTURE,),
    name="PloneAppIterate:Integration")

PLONEAPPITERATE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATE_FIXTURE,),
    name="PloneAppIterate:Functional")
