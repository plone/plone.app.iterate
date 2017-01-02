Changelog
=========

3.2.4 (2017-01-02)
------------------

Bug fixes:

- Cleanup: isort, zca decorators, etc.
  [jensens]

- Some more cleanup.
  [gforcada]

3.2.3 (2016-11-10)
------------------

Bug fixes:

- Add coding header on python files.
  [gforcada]

- Hide uninstall profile from being shown on the Plone install (advanced) form.
  [gforcada]

3.2.2 (2016-09-14)
------------------

Bug fixes:

- Remove broken references when making checkout.
  Fixes issue `30 <https://github.com/plone/plone.app.iterate/issues/30>`_.
  [maurits]


3.2.1 (2016-08-17)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


3.2.0 (2016-05-26)
------------------

New features:

- Added uninstall profile.  [maurits]

Bug fixes:

- Removed deprecated ``actionicons.xml``.  [maurits]


3.1.7 (2016-05-15)
------------------

Bug fixes:

- no special case that enables checkout via GET
  [gotcha]


3.1.6 (2016-04-26)
------------------

Fixes:

- Minimal code cleanup.  [gforcada]


3.1.5 (2016-03-03)
------------------

New:

- plone.app.iterate depends on GenericSetup >= 1.8.2
  for using a post_handler on registerProfile
  [iham]

- Added naming of default GenericSetup profile as "default".
  "plone.app.iterate" also exists to keep compatibility.
  [iham]

- Added deprecation warning to GS profile "plone.app.iterate"
  [iham]

Fixes:

- No need to register as Zope2 Product anymore.
  [iham]

- Some minor pep8 cleanup.
  [iham]

3.1.4 (2015-11-16)
------------------

Fixes:

- Keep the default page setting when checking in a document.
  [maurits]


3.1.3 (2015-09-27)
------------------

- Fix metadata storage for dexterity checkouts
  [vangheem]


3.1.2 (2015-09-20)
------------------

- Fixed test to pass with recent plone.app.content change
  that requires the cmf.ModifyPortalContent permission for the
  content_status_history page.
  [maurits]


3.1.1 (2015-08-20)
------------------

- Check if object does not have iterate policy. This fixes
  iterate causing toolbar errors on portal root.
  [vangheem]


3.1.0 (2015-07-18)
------------------

- Merge plone.app.stagingbehavior into plone.app.iterate without the
  behavior implementation. This is for Plone 5 iterate support.
  [vangheem]

- Don't remove aquisition on object for getToolByName call.
  [tomgross]


3.0.1 (2015-03-12)
------------------

- Add permission names zcml/z3 style and load permission settings explicit
  when module is loaded, otherwise default roles where not set correctly.
  [jensens]

- Ported tests to plone.app.testing
  [bogdan, tomgross]


3.0.0 (2014-10-23)
------------------

- Remove DL's from portal message in templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]


2.1.13 (2014-04-16)
-------------------

- Fix tests to work with auto csrf.
  [vangheem]

- Fix tests for latest plone.protect.
  [vangheem]


2.1.12 (2014-02-19)
-------------------

- Information messages can be hidden from user who checked out content when
  using a placeful workflow, see: https://dev.plone.org/ticket/13852
  [anthonygerrard]

- Replaced the "Locked" label with "Warning"
  [rristow]


2.1.11 (2014-01-27)
-------------------

- setted lock timeout to MAX_TIMEOUT to avoid baseline unwanted unlock after 10 minutes
  [parruc]


2.1.10 (2013-03-05)
-------------------

- Fixed error on checking in the working copy of an object linked in it's
  parent rich text field, see: https://dev.plone.org/ticket/13462
  [radekj]


2.1.9 (2013-01-13)
------------------

- Nothing changed yet.


2.1.8 (2012-10-03)
------------------

- Unmark both the baseline and the working copy on checkin so that dexterity
  content is properly unmarked.
  [cewing]


2.1.7 (2012-08-04)
------------------

- Allow browser view templates to be defined and thus overridden in ZCML.
  [rpatterson]


2.1.6 (2012-06-29)
------------------

- Import events from zope.lifecycleevent.
  [hannosch]

- Fix permissions check in parent folder working copy locator.
  [mitchellrj]


2.1.5 (2012-03-16)
------------------

- Don't declare IIterateAware as an extension of Archetypes' IReferenceable,
  because there are other implementations (such as the one for Dexterity)
  that don't use Archetypes references.
  [davisagli]

- Make sure permissions of working copy workflow get applied when checking
  out content, fixes http://dev.plone.org/ticket/12780
  [anthonygerrard]


2.1.4 (2011-11-24)
------------------

- Preserve content contents UIDs when checking a folder back in.  This
  prevents breaking linking by UID in the editor.
  [rossp]

- Fix a problem with items added to a checked out folder not being
  visible after checkin.  Fixes #12257.
  [rossp]

- Preserve the folder order position from the item originally checked
  out when checking it back in.
  [rossp]

- Allow user of check'd out content to also see the checkout info so
  a contributor can see that he already has a page checked out
  easily.
  [vangheem]


2.1.3 (2011-08-31)
------------------

- Remove rogue div tag from diff.pt. This fixes
  http://dev.plone.org/plone/ticket/11249
  [danjacka]

2.1.2 - 2011-06-02
------------------

- Include Products.CMFCore for Plone 4.1 compatibility.
  [thomasdesvenain, WouterVH]

2.1.1 - 2011-05-13
------------------

- Fixed an issue where our subscriber always expected a coci_created attribute
  to be available at the policy.
  [erico_andrei]

- Add MANIFEST.in.
  [WouterVH]

- Viewing a working copy or an original of a checkout does not raise
  AttributeError anymore. Anyway, we log a warning because a Manager should do
  something about this. Fixes http://dev.plone.org/plone/ticket/8723
  [glenfant]


2.1 - 2011-02-25
----------------

- No changes.


2.1a2 - 2011-02-14
------------------

- Fixed stale catalog entries appearing for references of merged
  content.
  [maurits]

- Fixed minor test failure for ``_doAddUser``.
  [maurits]


2.1a1 - 2011-01-18
------------------

- Test Products.CMFPlone version to set default permission, keeping 4.0
  compatibility - the next release can be 2.0.1 again.
  [elro]

- Add autoinclude entry point.
  [elro]

- Update permission defaults for Plone 4.1's Site Administrator role.
  [elro]


2.0 - 2010-07-18
----------------

- Fixed the info viewlet to show only the date, and not the time.
  The issue was introduced because ulocalized_time changed its parameters order.
  This closes http://dev.plone.org/plone/ticket/10759.
  [vincentfretin]

- Update license to GPL version 2 only.
  [hannosch]

- Add id="content" for the content divs. Else theming with deliverance gets
  harder.
  [do3cc]


2.0b2 - 2010-06-03
------------------

- Add naive upgrade step that reinstalls the product.
  [davisagli]

- Set action icons via icon_expr on the actions, to avoid deprecation warnings
  in Plone 4.
  [davisagli]


2.0b1 - 2010-02-17
------------------

- Declare all package dependencies.
  [hannosch]

- Updated diff.pt to follow recent markup conventions.
  References #9981
  [spliter]


1.2.5 - 2010-01-03
------------------

- Fixed an undefined ``current_page_url`` variable in diff.pt. This closes
  http://dev.plone.org/plone/ticket/9819.
  [hannosch]


1.2.4 - 2008-12-21
------------------

- Added profiles/default/metadata.xml (version 120: lets leave plenty room in
  case any profile changes are needed on the 1.1 branch).
  [maurits]

- Avoid a test dependency on quick installer.
  [hannosch]

- Use our own PloneMessageFactory. We don't depend on CMFPlone anymore.
  [hannosch]

- Specified package dependencies.
  [hannosch]

- Made the tests independent of default content.
  [hannosch]


1.2.3 - 2008-11-14
------------------

- Fix assumption in control view: not every context object is
  IReferenceable. This fixes http://dev.plone.org/plone/ticket/8737
  [nouri]


1.2.2 - 2008-11-13
------------------

- Fix action conditions for the nth time; this time it's an
  over-ambitious "Cancel check-out" permission.  This fixes
  http://dev.plone.org/plone/ticket/8735
  [nouri]


1.2.1 - 2008-11-11
------------------

- Refine permissions fix from 1.2.0 and make tests pass again:

  Don't require Modify Portal Content (MPC) permission on the
  original to check out, which was omitted in the fix for 1.2.0.

  Don't require MPC on the original for canceling of checkout, only
  require it on the working copy.
  [nouri]

- Fix missing internationalization (#8608 thanks to Vincent Fretin)
  [encolpe]


1.2.0 - 2008-10-24
------------------

- Allow users without modify content permissions (but with the iterate
  check out permission) to check out items, and only allow them to
  check in back again only when they have modify content permissions.
  [nouri]


1.1.5 - 2008-08-18
------------------

- Fixed typo in subscribers/workflow.py. This fixes
  https://dev.plone.org/plone/ticket/8035.
  [dunlapm]

- Added i18n of status messages. This fixes part of
  http://dev.plone.org/plone/ticket/8022.
  [naro]


1.1.0 - 2008-04-20
------------------

- Fixed dodgy test in test_iterate.py that was dependent on semantics of
  default workflow.
  [optilude]

- Fixed i18n markup and updated some messages. This closes
  http://dev.plone.org/plone/ticket/7958.
  [hannosch]

- Updated i18n:domain in templates to the plone domain. There's no need for a
  iterate domain.
  [hannosch]

- Use README.txt and HISTORY.txt for the package's long description.
  [wichert]

- Remove unneeded initialize method from __init__
  [wichert]


1.0 - 2007-08-17
----------------

- First release

.. _`#1451`: https://github.com/plone/Products.CMFPlone/issues/1451
