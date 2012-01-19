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

from ZenPacks.zenoss.CloudStack import BaseComponent


class SystemVM(BaseComponent):
    meta_type = portal_type = "SystemVM"

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

        if self.systemvm_type == 'consoleproxy':
            templates.append(self.getRRDTemplateByName('ConsoleProxy'))

        return templates

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
