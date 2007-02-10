##################################################################
#
# (C) Copyright 2006-2007 ObjectRealms, LLC
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
# along with CMFDeployment; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##################################################################
"""
$Id: locking.py 1824 2007-02-08 17:59:41Z hazmat $
"""

from plone.app.iterate import lock

def handleWCDeleted( event ):
    # may be called multiple times, must be reentrant
    lock.unlockContext( event.baseline )
    # we reindex to force a metadata update
    event.baseline.reindexObject( idxs=['review_state'] )
    
def handleCheckout( event ):
    lock.lockContext( event.object )
    event.object.reindexObject( idxs=['review_state'] )
    
def handleCancelCheckout( event ):
    lock.unlockContext( event.baseline )
    event.baseline.reindexObject( idxs=['review_state'] )    
        
    
