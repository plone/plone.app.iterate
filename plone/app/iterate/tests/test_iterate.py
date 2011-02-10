##################################################################
#
# (C) Copyright 2006 ObjectRealms, LLC
# All Rights Reserved
#
# This file is part of iterate.
#
# iterate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# iterate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with iterate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
$Id: test_iterate.py 1595 2006-08-24 00:15:21Z hazmat $
"""

from AccessControl import getSecurityManager

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy

from Products.PloneTestCase import PloneTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite
PloneTestCase.setupPloneSite()

class TestIterations(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager',])
        
        # Since we depend on ZCML being loaded, we can't do this
        # until the layer is set up

        self.portal.portal_setup.runAllImportStepsFromProfile(
            'profile-plone.app.iterate:plone.app.iterate')

        # add a folder with two documents in it
        self.portal.invokeFactory('Folder', 'docs')
        self.portal.docs.invokeFactory('Document', 'doc1')
        self.portal.docs.invokeFactory('Document', 'doc2')

        # add a working copy folder
        self.portal.invokeFactory('Folder', 'workarea')

        self.repo = self.portal.portal_repository
        self.wf   = self.portal.portal_workflow

    def beforeTearDown(self):
        self.repo = None
        self.wf   = None

    def shim_test( self, test_method):

        try:
            test_method()
        except:
            import sys, pdb, traceback
            ec, e, tb = sys.exc_info()
            traceback.print_exc()            
            pdb.post_mortem( tb )

    def test_workflowState( self ):
        # ensure baseline workflow state is retained on checkin, including security

        doc = self.portal.docs.doc1
        
        # sanity check that owner can edit visible docs
        self.setRoles(['Owner',])
        self.assertTrue( getSecurityManager().checkPermission( "Modify portal content",
                                                               self.portal.docs.doc1 ) )

        self.setRoles(['Manager',])        
        self.wf.doActionFor( doc, 'publish')
        state = self.wf.getInfoFor( doc, 'review_state')
        
        self.repo.save( doc )
        wc = ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )
        wc_state = self.wf.getInfoFor( wc, 'review_state')
        
        self.assertNotEqual( state, wc_state )

        ICheckinCheckoutPolicy( wc ).checkin( "modified" )
        bstate = self.wf.getInfoFor( wc, 'review_state')
        self.assertEqual( state, bstate )
        self.setRoles(['Owner',])       

    def test_baselineVersionCreated( self ):
        # if a baseline has no version ensure that one is created on checkout

        doc = self.portal.docs.doc1
        self.assertTrue( self.repo.isVersionable( doc ) )

        history = self.repo.getHistory( doc )
        self.assertEqual( len(history), 0 )

        ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )

        history = self.repo.getHistory( doc )
        self.assertEqual( len(history), 1 )

        doc2 = self.portal.docs.doc2
        self.repo.save( doc2 )

        ICheckinCheckoutPolicy( doc2 ).checkout( self.portal.workarea )

        history = self.repo.getHistory( doc2 )
        self.assertEqual( len(history), 1 )
    
    def test_wcNewForwardReferencesCopied( self ):
        # ensure that new wc references are copied back to the baseline on checkin
        doc = self.portal.docs.doc1
        doc.addReference( self.portal.docs )
        self.assertEqual( len(doc.getReferences("zebra")), 0)
        wc = ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )
        wc.addReference( self.portal.docs.doc2, "zebra")        
        doc = ICheckinCheckoutPolicy( wc ).checkin( "updated" )
        self.assertEqual( len(doc.getReferences("zebra")), 1 )
        
    def test_wcNewBackwardReferencesCopied( self ):
        # ensure that new wc back references are copied back to the baseline on checkin

        doc = self.portal.docs.doc1
        self.assertEqual( len(doc.getBackReferences("zebra")), 0)
        wc = ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )
        self.portal.docs.doc2.addReference( wc, "zebra")
        self.assertEqual( len( wc.getBackReferences("zebra")), 1 )        
        doc = ICheckinCheckoutPolicy( wc ).checkin( "updated")
        self.assertEqual( len( doc.getBackReferences("zebra")), 1 )

    def test_baselineReferencesMaintained( self ):
        # ensure that baseline references are maintained when the object is checked in
        # copies forward, bkw are not copied, but are maintained.

        doc = self.portal.docs.doc1
        doc.addReference( self.portal.docs, "elephant" )
        self.portal.docs.doc2.addReference( doc )

        wc = ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )

        doc = ICheckinCheckoutPolicy( wc ).checkin( "updated" )

        # TODO: This fails in Plone 4.1. The new optimized catalog lookups
        # in the reference catalog no longer filter out non-existing reference
        # objects. In both Plone 4.0 and 4.1 there's two references, one of
        # them is a stale catalog entry in the reference catalog. The real fix
        # is to figure out how the stale catalog entry gets in there
        self.assertEqual( len(doc.getReferences()), 1 )
        self.assertEqual( len(doc.getBackReferences()), 1 )

    def test_baselineNoCopyReferences( self ):
        # ensure that custom state is maintained with the no copy adapter

        # setup the named ref adapter
        from zope import component
        from Products.Archetypes.interfaces import IBaseObject
        from plone.app.iterate import relation, interfaces
        from plone.app.iterate.tests.utils import CustomReference
        
        component.provideAdapter( 
            adapts = (IBaseObject,),
            provides = interfaces.ICheckinCheckoutReference,
            factory = relation.NoCopyReferenceAdapter,
            name="zebra")

        doc = self.portal.docs.doc1
        ref = doc.addReference( self.portal.docs, "zebra", referenceClass=CustomReference )
        ref.custom_state = "hello world"

        wc = ICheckinCheckoutPolicy( doc ).checkout( self.portal.workarea )

        self.assertEqual( len(wc.getReferences("zebra")), 0)

        doc = ICheckinCheckoutPolicy( wc ).checkin( "updated" )

        self.assertEqual( len(doc.getReferences("zebra")), 1)

        ref = doc.getReferenceImpl("zebra")[0]

        self.assert_( hasattr( ref, "custom_state") )
        self.assertEqual( ref.custom_state, "hello world")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIterations))
    suite.addTest(FunctionalDocFileSuite(
        'browser.txt',
        test_class=PloneTestCase.FunctionalTestCase))
    return suite
