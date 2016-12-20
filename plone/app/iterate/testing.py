# -*- coding: utf-8 -*-
"""Testing setup for integration and functional tests."""
from plone.app.contenttypes.testing import PloneAppContenttypes
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.testing import z2


ADMIN = {
    'id': 'admin',
    'password': 'secret',
    'roles': ['Manager'],
}
EDITOR = {
    'id': 'editor',
    'password': 'secret',
    'roles': ['Editor'],
}
CONTRIBUTOR = {
    'id': 'contributor',
    'password': 'secret',
    'roles': ['Contributor'],
}
USERS_TO_BE_ADDED = (
    ADMIN,
    EDITOR,
    CONTRIBUTOR,
)
USERS_WITH_MEMBER_FOLDER = (
    EDITOR,
    CONTRIBUTOR,
)


class PloneAppIterateLayer(PloneSandboxLayer):
    """Plone Sandbox Layer for plone.app.iterate."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Setup Zope with Addons."""
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        z2.installProduct(app, 'Products.ATContentTypes')

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'plone.app.collection')

        import plone.app.iterate
        self.loadZCML(package=plone.app.iterate)

    def setUpPloneSite(self, portal):
        """Setup Plone Site with Addons."""
        # restore default workflow
        applyProfile(portal, 'Products.CMFPlone:testfixture')

        # add default content
        applyProfile(portal, 'Products.ATContentTypes:content')

        applyProfile(portal, 'plone.app.iterate:default')
        applyProfile(portal, 'plone.app.iterate:test')

        for user in USERS_TO_BE_ADDED:
            portal.portal_membership.addMember(
                user['id'],
                user['password'],
                user['roles'],
                [],
            )

        for user in USERS_WITH_MEMBER_FOLDER:
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
    name='PloneAppIterateLayer:Integration')

PLONEAPPITERATE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATE_FIXTURE,),
    name='PloneAppIterateLayer:Functional')


class DexPloneAppIterateLayer(PloneAppContenttypes):
    """Dexterity based Plone Sandbox Layer for plone.app.iterate."""

    def setUpZope(self, app, configurationContext):
        """Setup Zope with Addons."""
        super(DexPloneAppIterateLayer,
              self).setUpZope(app, configurationContext)

        import plone.app.iterate
        self.loadZCML(package=plone.app.iterate)

    def setUpPloneSite(self, portal):
        """Setup Plone Site with Addons."""
        super(DexPloneAppIterateLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'plone.app.iterate:default')


PLONEAPPITERATEDEX_FIXTURE = DexPloneAppIterateLayer()
PLONEAPPITERATEDEX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,),
    name='DexPloneAppIterateLayer:Integration')

PLONEAPPITERATEDEX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,),
    name='DexPloneAppIterateLayer:Functional')
