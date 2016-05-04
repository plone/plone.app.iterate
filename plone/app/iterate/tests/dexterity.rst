Staging behavior regression tests
=================================

Tests for bugs that would distract from usage examples in stagingbehavior.txt

If we access the site as an admin TTW::

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(layer["app"])
    >>> browser.handleErrors = False
    >>> portal = layer["portal"]
    >>> portal_url = "http://nohost/plone"
    >>> from plone.app.testing.interfaces import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser.addHeader("Authorization", "Basic %s:%s" % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))

KeyError with aquisition wrapper
=========================================

When an item provides IBaseline (has been checked in at least once) and it is accessed through an
Aquisition wrapper you get a KeyError from zope.intid, originating from five.intid.

    >>> browser.open(portal_url + "/folder_factories")
    >>> browser.getControl("Folder").click()
    >>> browser.getControl("Add").click()
    >>> browser.getControl(name="form.widgets.IDublinCore.title").value = "My Folder"
    >>> browser.getControl(name="form.buttons.save").click()
    >>> browser.url
    'http://nohost/plone/my-folder/view'

    >>> browser.open("http://nohost/plone/my-folder/folder_factories")
    >>> browser.getControl("Page").click()
    >>> browser.getControl("Add").click()
    >>> browser.getControl(name="form.widgets.IDublinCore.title").value = "My Sub-object"
    >>> browser.getControl(name="form.buttons.save").click()
    >>> browser.url
    'http://nohost/plone/my-folder/my-sub-object/view'

Checkout

    >>> browser.getLink("Check out").click()
    >>> 'form.button.Checkout' in browser.contents
    True
    >>> browser.getControl(name='form.button.Checkout').click()
    >>> browser.contents
    '...This is a working copy of...My Sub-object..., made by...admin... on...'

Checkin

    >>> browser.getLink("Check in").click()
    >>> browser.contents
    '...Check in...'
    >>> browser.getControl(name="form.button.Checkin").click()
    >>> browser.url
    'http://nohost/plone/my-folder/my-sub-object'

Test can view through Aquisition wrapper (repeating test_folder is deliberate here)

    >>> browser.open("http://nohost/plone/my-folder/my-sub-object")
    >>> browser.contents
    '...My Sub-object...'
