###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2013, Zenoss Inc.
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
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from Products.ZenUtils.Search import makeFieldIndex, makeKeywordIndex
from Products.ZenUtils.Utils import zenPath, unused

unused(Globals)


ZENPACK_NAME = 'ZenPacks.zenoss.CloudStack'

# Modules containing model classes. Used by zenchkschema to validate
# bidirectional integrity of defined relationships.
productNames = (
    'Cloud',
    'Cluster',
    'Host',
    'Pod',
    'RouterVM',
    'SystemVM',
    'VirtualMachine',
    'Zone',
    )

# Useful to avoid making literal string references to module and class names
# throughout the rest of the ZenPack.
MODULE_NAME = {}
CLASS_NAME = {}

for product_name in productNames:
    MODULE_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name])
    CLASS_NAME[product_name] = '.'.join([ZENPACK_NAME, product_name, product_name])

setzPropertyCategory('zCloudStackURL', 'CloudStack')
setzPropertyCategory('zCloudStackAPIKey', 'CloudStack')
setzPropertyCategory('zCloudStackSecretKey', 'CloudStack')


class ZenPack(ZenPackBase):
    packZProperties = [
        ('zCloudStackURL', '', 'string'),
        ('zCloudStackAPIKey', '', 'string'),
        ('zCloudStackSecretKey', '', 'password'),
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


class CatalogMixin(object):
    '''
    Abstract class mixin to ease the creation and use of
    component-specific catalogs.

    To use this mixin to create a component catalog you should define
    a _catalog property such as the following on your mixed-in class::

        _catalogs = dict({
            'catalogName', {
                'deviceclass': '/Example/Device/Class',
                'indexes': {
                    'ipv4_addresses': {'type': 'keyword'},
                    'mac_addresses': {'type': 'keyword'},
                    },
                },
            }, **BaseClass._catalogs)

    The second item in each indexes tuple can either be keyword or
    field. These correspond to Zope case-insensitive KeywordIndex and
    FieldIndex.
    '''

    _catalogs = {}

    @classmethod
    def _catalog_spec(cls, name):
        spec = cls._catalogs.get(name)
        if not spec:
            LOG.error("%s catalog definition is missing", name)
            return

        if not isinstance(spec, dict):
            LOG.error("%s catalog definition is not a dict", name)
            return

        if not spec.get('indexes'):
            LOG.error("%s catalog definition has no indexes", name)
            return

        if not spec.get('deviceclass'):
            LOG.error("%s catalog definition has no deviceclass.", name)
            return

        return spec

    @classmethod
    def _create_catalog(cls, dmd, name):
        from Products.ZCatalog.Catalog import CatalogError
        from Products.ZCatalog.ZCatalog import manage_addZCatalog

        from Products.Zuul.interfaces import ICatalogTool

        spec = cls._catalog_spec(name)
        if not spec:
            return

        deviceclass = dmd.Devices.createOrganizer(spec['deviceclass'])

        if not hasattr(deviceclass, name):
            manage_addZCatalog(deviceclass, name, name)

        zcatalog = deviceclass._getOb(name)
        catalog = zcatalog._catalog

        for propname, propdata in spec['indexes'].items():
            index_type = propdata.get('type')
            if not index_type:
                LOG.error("%s index has no type", propname)
                return

            index_factory = {
                'field': makeFieldIndex,
                'keyword': makeKeywordIndex,
                }.get(index_type.lower())

            if not index_factory:
                LOG.error("%s is not a valid index type", index_type)
                return

            try:
                catalog.addIndex(propname, index_factory(propname))
            except CatalogError:
                # Index already exists.
                pass
            else:
                fqcn = '.'.join((cls.__module__, cls.__name__))
                results = ICatalogTool(dmd.primaryAq()).search(fqcn)
                for brain in results:
                    brain.getObject().index_object()

        return zcatalog

    @classmethod
    def _get_catalog(cls, dmd, name):
        spec = cls._catalog_spec(name)
        if not spec:
            return

        deviceclass = dmd.Devices.createOrganizer(spec['deviceclass'])

        try:
            return getattr(deviceclass, name)
        except AttributeError:
            return cls._create_catalog(dmd, name)

    @classmethod
    def search(cls, dmd, name, **kwargs):
        '''
        Generate instances of this object that match keyword arguments.
        '''
        catalog = cls._get_catalog(dmd, name)
        if not catalog:
            return

        for brain in catalog(**kwargs):
            yield brain.getObject()

    def index_object(self, idxs=None):
        '''
        Index the mixed-in instance in its catalogs.

        We rely on subclasses to explicitely call this method in
        addition to their primary inheritence index_object method as in
        the following override::

            def index_object(self, idxs=None):
                for superclass in (ManagedEntity, CatalogMixin):
                    superclass.index_object(self, idxs=idxs)
        '''
        for catalog in (self._get_catalog(self.dmd, x) for x in self._catalogs):
            catalog.catalog_object(self, self.getPrimaryId())

    def unindex_object(self):
        '''
        Unindex the mixed-in instance from its catalogs.

        We rely on subclasses to explicitely call this method in
        addition to their primary inheritence unindex_object method as
        in the following override::

            def unindex_object(self):
                for superclass in (ManagedEntity, CatalogMixin):
                    superclass.unindex_object(self)
        '''
        for catalog in (self._get_catalog(self.dmd, x) for x in self._catalogs):
            catalog.uncatalog_object(self.getPrimaryId())


class BaseComponent(DeviceComponent, ManagedEntity, CatalogMixin):
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

    def index_object(self, idxs=None):
        '''
        Index object according to ManagedEntity and CatalogMixin.
        '''
        for superclass in (ManagedEntity, CatalogMixin):
            superclass.index_object(self, idxs=idxs)

    def unindex_object(self):
        '''
        Unindex object according to ManagedEntity and CatalogMixin.
        '''
        for superclass in (ManagedEntity, CatalogMixin):
            superclass.unindex_object(self)

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
