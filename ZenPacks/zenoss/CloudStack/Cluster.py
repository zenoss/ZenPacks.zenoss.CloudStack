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

from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from ZenPacks.zenoss.CloudStack import BaseComponent


class Cluster(BaseComponent):
    meta_type = portal_type = "CloudStackCluster"

    cluster_type = None
    hypervisor_type = None
    managed_state = None

    _properties = BaseComponent._properties + (
        {'id': 'cluster_type', 'type': 'string', 'mode': ''},
        {'id': 'hypervisor_type', 'type': 'string', 'mode': ''},
        {'id': 'managed_state', 'type': 'string', 'mode': ''},
        )

    _relations = BaseComponent._relations + (
        ('pod', ToOne(ToManyCont,
            'ZenPacks.zenoss.CloudStack.Pod.Pod',
            'clusters')
            ),

        ('hosts', ToManyCont(ToOne,
            'ZenPacks.zenoss.CloudStack.Host.Host',
            'cluster')
            ),
        )

    def device(self):
        return self.pod().device()
