###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012-2013, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne

from ZenPacks.zenoss.CloudStack import BaseComponent, TouchTestMixin
from ZenPacks.zenoss.CloudStack.utils import require_zenpack


class RouterVM(BaseComponent, TouchTestMixin):
    meta_type = portal_type = "CloudStackRouterVM"

    account = None
    created = None
    dns1 = None
    dns2 = None
    domain = None
    gateway = None
    guest_ip = None
    guest_macaddress = None
    guest_netmask = None
    linklocal_ip = None
    linklocal_macaddress = None
    linklocal_netmask = None
    network_domain = None
    public_ip = None
    public_macaddress = None
    public_netmask = None
    state = None
    template_id = None

    _properties = BaseComponent._properties + (
        {'id': 'account', 'type': 'string', 'mode': 'w'},
        {'id': 'created', 'type': 'string', 'mode': 'w'},
        {'id': 'dns1', 'type': 'string', 'mode': 'w'},
        {'id': 'dns2', 'type': 'string', 'mode': 'w'},
        {'id': 'domain', 'type': 'string', 'mode': 'w'},
        {'id': 'gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'guest_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'guest_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'guest_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'network_domain', 'type': 'string', 'mode': 'w'},
        {'id': 'public_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'public_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'public_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'state', 'type': 'string', 'mode': 'w'},
        {'id': 'template_id', 'type': 'int', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('pod', ToOne(ToManyCont,
            'ZenPacks.zenoss.CloudStack.Pod.Pod',
            'routervms')
            ),

        ('host', ToOne(ToMany,
            'ZenPacks.zenoss.CloudStack.Host.Host',
            'routervms')
            ),
        )

    _catalogs = {
        'RouterVMCatalog': {
            'deviceclass': '/CloudStack',
            'indexes': {
                'ipv4_addresses': {'type': 'keyword'},
                'mac_addresses': {'type': 'keyword'},
                },
            },
        }

    @property
    def ipv4_addresses(self):
        return filter(
            lambda x: x, (
                self.guest_ip,
                self.linklocal_ip,
                self.public_ip))

    @property
    def mac_addresses(self):
        return filter(
            lambda x: x, (
                self.guest_macaddress,
                self.linklocal_macaddress,
                self.public_macaddress))

    @classmethod
    def findByIP(cls, dmd, ipv4_addresses):
        '''
        Return the first RouterVM matching one of ipv4_addresses.
        '''
        return next(cls.search(
            dmd, 'RouterVMCatalog', ipv4_addresses=ipv4_addresses), None)

    @classmethod
    def findByMAC(cls, dmd, mac_addresses):
        '''
        Return the first RouterVM matching one of mac_addresses.
        '''
        return next(cls.search(
            dmd, 'RouterVMCatalog', mac_addresses=mac_addresses), None)

    def device(self):
        return self.pod().device()

    def setHostId(self, host_id):
        for cluster in self.pod.clusters():
            for host in cluster.hosts():
                if host_id == host.cloudstack_id:
                    self.host.addRelation(host)
                    return

    def getHostId(self):
        host = self.host()
        if host:
            return host.cloudstack_id

    def getRRDTemplates(self):
        templates = super(BaseComponent, self).getRRDTemplates()
        templates.extend(self.extra_templates())

        return templates

    @require_zenpack('ZenPacks.zenoss.XenServer')
    def xenserver_vm(self):
        from ZenPacks.zenoss.XenServer.VIF import VIF

        vif = VIF.findByMAC(self.dmd, mac_addresses=self.mac_addresses)
        if vif:
            return vif.vm()
