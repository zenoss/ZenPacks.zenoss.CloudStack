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
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zCloudStackURL', '', 'string'),
        ('zCloudStackAPIKey', '', 'string'),
        ('zCloudStackSecretKey', '', 'string'),
        ]

    _plugins = (
        'poll_cloudstack.py',
        )

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlink_plugins()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.remove_plugin_symlinks()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlink_plugins(self):
        for plugin in self._plugins:
            LOG.info('Linking %s plugin into $ZENHOME/libexec/', plugin)
            plugin_path = zenPath('libexec', plugin)
            os.system('ln -sf "%s" "%s"' % (self.path(plugin), plugin_path))
            os.system('chmod 0755 %s' % plugin_path)

    def remove_plugin_symlinks(self):
        for plugin in self._plugins:
            LOG.info('Removing %s link from $ZENHOME/libexec/', plugin)
            os.system('rm -f "%s"' % zenPath('libexec', plugin))


class BaseComponent(DeviceComponent, ManagedEntity):
    """
    Abstract base class to avoid repeating boilerplate code in all of the
    DeviceComponent subclasses in this ZenPack.
    """

    # All CloudStack components have these properties.
    cloudstack_id = None
    allocation_state = None

    _properties = ManagedEntity._properties + (
        {'id': 'cloudstack_id', 'type': 'int', 'mode': ''},
        {'id': 'allocation_state', 'type': 'string', 'mode': ''},
        )

    # Disambiguate multi-inheritence.
    _relations = ManagedEntity._relations

    # This makes the "Templates" component display available.
    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    # Query for events by id instead of name.
    event_key = "ComponentId"


# We need to filter CloudStack components by id instead of name.
EventManagerBase.ComponentIdWhere = (
    "\"(device = '%s' and component = '%s')\""
    " % (me.device().getDmdKey(), me.id)")
