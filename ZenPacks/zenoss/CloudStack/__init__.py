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

import Globals

from Products.ZenEvents.EventManagerBase import EventManagerBase
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath, unused

unused(Globals)


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
        # We expect the /Capacity event class to exist, but don't want to add
        # it into objects.xml in case someone removes this ZenPack.
        app.zport.dmd.Events.createOrganizer('/Capacity')

        super(ZenPack, self).install(app)
        self.symlink_plugins()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.remove_plugin_symlinks()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlink_plugins(self):
        libexec = os.path.join(os.environ.get('ZENHOME'), 'libexec')
        if not os.path.isdir(libexec):
            # Stack installs might not have a $ZENHOME/libexec directory.
            os.mkdir(libexec)

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

    def getIconPath(self):
        return '/++resource++cloudstack/img/cloudstack.png'


class TouchTestMixin(object):
    """Common code for objects that support a "touch test"."""

    def ssh_prefix(self):
        """SSH prefix for connecting to system VMs through their host.

        This is necessary because system VMs are only able to be connected to
        via SSH through their link-local IP address. The only server that can
        reach the link-local IP is the host that the VM is currently running on.

        """

        host_ip = None
        host = self.host()
        if host and host.ip_address:
            host_ip = host.ip_address
        else:
            # From TEST-NET. Should never be a real IP address.
            host_ip = '192.0.2.1'

        key_option = None
        if self.primaryAq().zKeyPath:
            key_option = '-i %s' % self.primaryAq().zKeyPath
        else:
            key_option = ''

        user_prefix = None
        if self.primaryAq().zCommandUsername:
            user_prefix = '%s@' % self.primaryAq().zCommandUsername
        else:
            user_prefix = ''

        connect_timeout = None
        if self.primaryAq().zCommandCommandTimeout:
            connect_timeout = int(self.primaryAq().zCommandCommandTimeout) / 2
        else:
            connect_timeout = 30

        ssh_options = (
            "-q ",
            "-o ConnectTimeout=%s" % connect_timeout,
            "-o StrictHostKeyChecking=no",
            "-o UserKnownHostsFile=/dev/null",
            )

        context = {
            'key_option': key_option,
            'user_prefix': user_prefix,
            'ssh_options': ' '.join(ssh_options),
            'host_ip': host_ip,
            'linklocal_ip': self.linklocal_ip,
            }

        return (
            "ssh %(key_option)s %(ssh_options)s "
            "%(user_prefix)s%(host_ip)s "
            "ssh -i /root/.ssh/id_rsa.cloud -p3922 %(ssh_options)s "
            "root@%(linklocal_ip)s" % context)

    def touch_test_command(self):
        """Command template for touching and removing a file."""
        return (
            '/usr/bin/env sh -c \''
            '%s "touch zenosstest \&\& rm zenosstest" '
            '&& echo "file touched successfully" || '
            '(echo "file touch failed" ; false)\' '
            '2>/dev/null' % self.ssh_prefix())

    def extra_templates(self):
        templates = []

        host = self.host()
        if host and host.hypervisor == 'KVM':
            file_touch = self.getRRDTemplateByName("CloudStackFileTouch")
            if file_touch:
                templates.append(file_touch)

        return templates


# We need to filter CloudStack components by id instead of name.
EventManagerBase.ComponentIdWhere = (
    "\"(device = '%s' and component = '%s')\""
    " % (me.device().getDmdKey(), me.id)")
