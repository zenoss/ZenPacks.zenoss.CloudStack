###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, 2012 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from ZenPacks.zenoss.CloudStack import BaseComponent


class Pod(BaseComponent):
    meta_type = portal_type = "Pod"

    start_ip = None
    end_ip = None
    netmask = None
    gateway = None

    _properties = BaseComponent._properties + (
        {'id': 'start_ip', 'type': 'string', 'mode': ''},
        {'id': 'end_ip', 'type': 'string', 'mode': ''},
        {'id': 'netmask', 'type': 'string', 'mode': ''},
        {'id': 'gateway', 'type': 'string', 'mode': ''},
        )

    _relations = BaseComponent._relations + (
        ('zone', ToOne(ToManyCont,
            'ZenPacks.zenoss.CloudStack.Zone.Zone',
            'pods')
            ),

        ('clusters', ToManyCont(ToOne,
            'ZenPacks.zenoss.CloudStack.Cluster.Cluster',
            'pod')
            ),

        ('systemvms', ToManyCont(ToOne,
            'ZenPacks.zenoss.CloudStack.SystemVM.SystemVM',
            'pod')
            ),

        ('routervms', ToManyCont(ToOne,
            'ZenPacks.zenoss.CloudStack.RouterVM.RouterVM',
            'pod')
            ),
        )

    def device(self):
        return self.zone().device()
