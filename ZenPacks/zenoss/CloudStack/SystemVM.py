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


class SystemVM(BaseComponent, TouchTestMixin):
    meta_type = portal_type = "CloudStackSystemVM"

    gateway = None
    linklocal_ip = None
    linklocal_macaddress = None
    linklocal_netmask = None
    network_domain = None
    private_ip = None
    private_macaddress = None
    private_netmask = None
    public_ip = None
    public_macaddress = None
    public_netmask = None
    systemvm_type = None
    template_id = None

    _properties = BaseComponent._properties + (
        {'id': 'gateway', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'linklocal_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'network_domain', 'type': 'string', 'mode': 'w'},
        {'id': 'private_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'private_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'private_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'public_ip', 'type': 'string', 'mode': 'w'},
        {'id': 'public_macaddress', 'type': 'string', 'mode': 'w'},
        {'id': 'public_netmask', 'type': 'string', 'mode': 'w'},
        {'id': 'systemvm_type', 'type': 'string', 'mode': 'w'},
        {'id': 'template_id', 'type': 'int', 'mode': 'w'},
        )

    _relations = BaseComponent._relations + (
        ('pod', ToOne(ToManyCont,
            'ZenPacks.zenoss.CloudStack.Pod.Pod',
            'systemvms')
            ),

        ('host', ToOne(ToMany,
            'ZenPacks.zenoss.CloudStack.Host.Host',
            'systemvms')
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

        file_touch = self.getRRDTemplateByName("CloudStackFileTouch")
        if file_touch:
            templates.append(file_touch)

        if self.systemvm_type == 'consoleproxy':
            console_proxy = self.getRRDTemplateByName('CloudStackConsoleProxy')
            if console_proxy:
                templates.append(console_proxy)

        return templates
