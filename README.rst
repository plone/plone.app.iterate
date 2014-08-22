Summary
=======

iterate is a Plone add-on that allows one to utilize a checkin / checkout
procedure for content editing. It integrates in versioning, locking, and
utilizes Zope technology like adapters and events to allow for easy
customization.

Features
========

  - versioning utilizing cmf editions
  - locking using zope dav locks
  - pluggable behavior for policies via adapters
  - observable behavior via events
  - specialized handling for archetypes references
  - simple, clean integration with the plone user interface

Use Cases
=========

iterate was designed to solve/enable the following use cases.

Collaborative Document Editing Scenario
---------------------------------------

Workgroup or person working on a document, the ability to checkout and lock a document
allows for a editing cycle, without concern of overwrites, and with an audit trail of
versions.

Publish/Modify/Review Cycles on a CMS
-------------------------------------

A common theme in content management, is publishing a web document, and then needing
to revise it but not to change the published web content, till the modified document
has undergone a review cycle.

Iterate Lifecycle via the User Interface
========================================

iterate integrates with the plone user interface mainly through the actions menu.
it adds three conditional actions to the menu.. checkout, checkin, and cancel checkout.

checkout form
-------------

on this form a user is asked to which location they wish to checkout
the current content, the vocabulary of checkouts is overridable via template
customization and is currently the current folder, and the user's home
folder. if the content is not yet versioned, versioning is applied and
a new version is created before the checkout is performed. an adapter
is utilized to perform the checkout mechanics and an object lifecycle
event is generated with the baseline ( origin ) and checkout as
attributes. the adapter is responsible for effecting a copy of the
content to the checkout location and taking a lock on the origin content.
whether this form and action are active on a given piece of content
depends on the iterate policy adapter found for this content.

checkouts have some system additional properties, versioning and workflow.
they can be versioned independently of the baseline, with only changes
from the latest version being merged into the baseline on
checkin. they can undergoe separate workflows different from the
baseline content. (this last feature requires some customization see
docs/workflow.rst ).

checkout status form
--------------------

visually checkouts are distinguished by an extra document icon (next
to sendto, and rss links). clicking on this icon will lead to a
checkout status page. which allows for looking at information
regarding the checkout itself, such as when the checkout was
performed and by whom.

checkin form
------------

a user is asked for a checkin message. on checkin the working copy is
merged into the baseline, and a new version of the baseline is
created, and the baseline is unlocked.

cancel checkout
---------------

a confirmation dialog is displayed, if the checkout is canceled the
working copy is destroyed, and the baseline is unlocked.


Credits
=======

 Kapil Thangavelu <hazmat@objectrealms.net>

 Benjamin Saller <bcsaller@objectrealms.net>

 icons from tortoisesvn project ( http://tigris.org )

License
=======

 GPL, see license.txt for details
