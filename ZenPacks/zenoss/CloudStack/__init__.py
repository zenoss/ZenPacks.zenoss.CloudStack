###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
LOG = logging.getLogger('zen.CloudStack')

import os

from Products.ZenEvents.EventManagerBase import EventManagerBase
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zCloudStackURL', '', 'string'),
        ('zCloudStackAPIKey', '', 'string'),
        ('zCloudStackSecretKey', '', 'string'),
        ]

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlinkPlugin()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.removePluginSymlink()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlinkPlugin(self):
        LOG.info('Linking poll_cloudstack.py plugin into $ZENHOME/libexec/')
        plugin_path = zenPath('libexec', 'poll_cloudstack.py')
        os.system('ln -sf "%s" "%s"' % (
            self.path('libexec', 'poll_cloudstack.py'), plugin_path))

        os.system('chmod 0755 %s' % plugin_path)

    def removePluginSymlink(self):
        LOG.info('Removing poll_cloudstack.py link from $ZENHOME/libexec/')
        os.system('rm -f "%s"' % zenPath('libexec', 'poll_cloudstack.py'))

# We need to filter CloudStack components by id instead of name.
EventManagerBase.ComponentIdWhere = (
    "\"(device = '%s' and component = '%s')\""
    " % (me.device().getDmdKey(), me.id)")
