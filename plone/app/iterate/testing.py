"""Testing setup for integration and functional tests."""

from plone.app.contenttypes.testing import PloneAppContenttypes
from plone.app.testing import applyProfile
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting


ADMIN = {
    "id": "admin",
    "password": "secret",
    "roles": ["Manager"],
}
EDITOR = {
    "id": "editor",
    "password": "secret",
    "roles": ["Editor"],
}
CONTRIBUTOR = {
    "id": "contributor",
    "password": "secret",
    "roles": ["Contributor"],
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


class DexPloneAppIterateLayer(PloneAppContenttypes):
    """Dexterity based Plone Sandbox Layer for plone.app.iterate."""

    def setUpZope(self, app, configurationContext):
        """Setup Zope with Addons."""
        super().setUpZope(app, configurationContext)

        import plone.app.iterate
        import plone.app.iterate.tests

        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=plone.app.iterate.tests)

    def setUpPloneSite(self, portal):
        """Setup Plone Site with Addons."""
        super().setUpPloneSite(portal)
        applyProfile(portal, "plone.app.iterate:default")
        applyProfile(portal, "plone.app.iterate.tests:testingdx")
        # with named AND dotted behaviors we need to take care of both
        versioning_behavior = {
            "plone.app.versioningbehavior.behaviors.IVersionable",
            "plone.versioning",
        }

        # Disable automatic versioning of Documents.  Note that Documents are
        # still versionable after this.  You just need to do it explicitly,
        # like plone.app.iterate does when needed.
        fti = portal.portal_types["Document"]
        # write back the behaviors without the versioning behaviors
        # using a Set to keep it simple
        # a = set((1,2,3))
        # b = set([2,4])
        # res = tuple(a.difference(b)) >> (1,3)
        fti.behaviors = tuple(
            set(fti.behaviors).difference(versioning_behavior),
        )


PLONEAPPITERATEDEX_FIXTURE = DexPloneAppIterateLayer()
PLONEAPPITERATEDEX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,), name="DexPloneAppIterateLayer:Integration"
)

PLONEAPPITERATEDEX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPITERATEDEX_FIXTURE,), name="DexPloneAppIterateLayer:Functional"
)
