# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PloneAppContenttypes
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.testing import z2


admin = {
    'id': 'admin',
    'password': 'secret',
    'roles': ['Manager'],
}
editor = {
    'id': 'editor',
    'password': 'secret',
    'roles': ['Editor'],
}
contributor = {
    'id': 'contributor',
    'password': 'secret',
    'roles': ['Contributor'],
}
users_to_be_added = (
    admin,
    editor,
    contributor,
)
users_with_member_folder = (
    editor,
    contributor,
)


class PloneAppIterateLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        z2.installProduct(app, 'Products.ATContentTypes')

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'plone.app.collection')

        import plone.app.iterate
        self.loadZCML(package=plone.app.iterate)
        z2.installProduct(app, 'plone.app.iterate')

    def setUpPloneSite(self, portal):
        # restore default workflow
        applyProfile(portal, 'Products.CMFPlone:testfixture')

        # add default content
        applyProfile(portal, 'Products.ATContentTypes:content')

        applyProfile(portal, 'plone.app.iterate:plone.app.iterate')
        applyProfile(portal, 'plone.app.iterate:test')

        for user in users_to_be_added:
            portal.portal_membership.addMember(
                user['id'],
                user['password'],
                user['roles'],
                [],
            )

        for user in users_with_member_folder:
            mtool = portal.portal_membership
            if not mtool.getMemberareaCreationFlag():
                mtool.setMemberareaCreationFlag()
                mtool.createMemberArea(user['id'])

            if mtool.getMemberareaCreationFlag():
                mtool.setMemberareaCreationFlag()

        portal.portal_workflow.setChainForPortalTypes(
            ('Document',),
            'plone_workflow',
        )

        # Turn on versioning for folders
        portal_repository = portal.portal_repository
        portal_repository.addPolicyForContentType(
            'Folder',
            u'at_edit_autoversion',
        )
        portal_repository.addPolicyForContentType(
            'Folder',
            u'version_on_revert',
        )
        versionable_types = portal_repository.getVersionableContentTypes()
        versionable_types.append('Folder')
        portal_repository.setVersionableContentTypes(versionable_types)


PLONEAPPITERATE_FIXTURE = PloneAppIterateLayer()

PLONEAPPITERATE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPITERATE_FIXTURE,),
    name="PloneAppIterateLayer:Integration")

PLONEAPPITERATE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATE_FIXTURE,),
    name="PloneAppIterateLayer:Functional")


class DexPloneAppIterateLayer(PloneAppContenttypes):
    def setUpZope(self, app, configurationContext):
        super(DexPloneAppIterateLayer, self).setUpZope(app, configurationContext)
        import plone.app.iterate
        self.loadZCML(package=plone.app.iterate)
        z2.installProduct(app, 'plone.app.iterate')

    def setUpPloneSite(self, portal):
        super(DexPloneAppIterateLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'plone.app.iterate:plone.app.iterate')


PLONEAPPITERATEDEX_FIXTURE = DexPloneAppIterateLayer()
PLONEAPPITERATEDEX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,),
    name="DexPloneAppIterateLayer:Integration")

PLONEAPPITERATEDEX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,),
    name="DexPloneAppIterateLayer:Functional")
