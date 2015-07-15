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
"""

import logging
from zope.i18nmessageid import MessageFactory
from plone.app.iterate import permissions  # noqa

PloneMessageFactory = MessageFactory('plone')
logger = logging.getLogger('plone.app.iterate')


try:
    import plone.app.relationfield  # noqa
except ImportError:
    logger.warn('Dexterity support for iterate is not available. '
                'You must install plone.app.relationfield')


try:
    import plone.app.stagingbehavior  # noqa
    logger.error('plone.app.stagingbehavior should NOT be installed with this version '
                 'of plone.app.iterate. You may experience problems running this configuration. '
                 'plone.app.iterate now has dexterity suport built-in.')
except ImportError:
    pass