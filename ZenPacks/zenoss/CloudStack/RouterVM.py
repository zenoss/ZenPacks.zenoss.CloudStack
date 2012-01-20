###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2012, Zenoss Inc.
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

        file_touch = self.getRRDTemplateByName("FileTouch")
        if file_touch:
            templates.append(file_touch)

        return templates
