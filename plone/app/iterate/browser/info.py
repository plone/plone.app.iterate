"""
$Id: base.py 1808 2007-02-06 11:39:11Z hazmat $
"""

from zope.interface import implements

from zope.viewlet.interfaces import IViewlet

from DateTime import DateTime
from AccessControl import getSecurityManager

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from plone.app.iterate.util import get_storage
from plone.app.iterate.interfaces import keys

from plone.app.iterate.relation import WorkingCopyRelation

from plone.memoize.instance import memoize

class BaseInfoViewlet( BrowserView ):
    
    implements( IViewlet )
    
    def __init__( self, context, request, view, manager ):
        super( BaseInfoViewlet, self ).__init__( context, request )
        self.__parent__ = view
        self.view = view
        self.manager = manager
        
    def update( self ):
        pass
    
    def render( self ):
        raise NotImplementedError
        
    @memoize
    def created( self ):
        time = self.properties.get( keys.checkout_time, DateTime() )
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, context=self.context, domain='plonelocales')

    @memoize
    def creator( self ):
        user_id = self.properties.get( keys.checkout_user )
        membership = getToolByName(self.context, 'portal_membership')
        if not user_id:
            return membership.getAuthenticatedMember()
        return membership.getMemberById( user_id )
        
    @memoize
    def creator_url( self ):
        creator = self.creator()
        portal_url = getToolByName(self.context, 'portal_url')
        return "%s/author/%s" % ( portal_url(), creator.getId() )
        
    @memoize
    def creator_name( self ):
        creator = self.creator()
        return creator.getProperty('fullname') or creator.getId()

    @property
    @memoize
    def properties( self ):
        wc_ref = self._getReference()
        if wc_ref is not None:
            return get_storage( wc_ref )
        else:
            return {}

    def _getReference( self ):
        raise NotImplemented
        
class BaselineInfoViewlet( BaseInfoViewlet ):
    
    template = ViewPageTemplateFile('info_baseline.pt')

    def render(self):
        if self.working_copy() is not None and \
            getSecurityManager().checkPermission(ModifyPortalContent, self.context):
            return self.template()
        else:
            return ""

    @memoize
    def working_copy( self ):
        refs = self.context.getBRefs( WorkingCopyRelation.relationship )
        if len( refs ) > 0:
            return refs[0]
        else:
            return None

    def _getReference( self ):
        refs = self.context.getBackReferenceImpl( WorkingCopyRelation.relationship )
        if len( refs ) > 0:
            return refs[0]
        else:
            return None
        
class CheckoutInfoViewlet( BaseInfoViewlet ):
    
    template = ViewPageTemplateFile('info_checkout.pt')
    
    def render(self):
        if self.baseline() is not None and \
            getSecurityManager().checkPermission(ModifyPortalContent, self.context):
            return self.template()
        else:
            return ""
    
    @memoize
    def baseline( self ):
        refs = self.context.getReferences( WorkingCopyRelation.relationship )
        if len( refs ) > 0:
            return refs[0]
        else:
            return None
    
    def _getReference( self ):
        refs = self.context.getReferenceImpl( WorkingCopyRelation.relationship )
        if len( refs ) > 0:
            return refs[0]
        else:
            return None
        
