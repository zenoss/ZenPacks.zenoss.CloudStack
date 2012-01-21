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

from zope.component import adapts

from ZenPacks.zenoss.DynamicView import TAG_IMPACTED_BY, TAG_IMPACTS, TAG_ALL
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider
from ZenPacks.zenoss.DynamicView.model.adapters import DeviceComponentRelatable

from ZenPacks.zenoss.CloudStack.Cloud import Cloud
from ZenPacks.zenoss.CloudStack.Zone import Zone
from ZenPacks.zenoss.CloudStack.Pod import Pod
from ZenPacks.zenoss.CloudStack.Cluster import Cluster
from ZenPacks.zenoss.CloudStack.Host import Host


### IRelatable Adapters

class CloudRelatable(BaseRelatable):
    adapts(Cloud)

    group = 'CloudStack'


class ZoneRelatable(DeviceComponentRelatable):
    adapts(Zone)

    group = 'CloudStack'


class PodRelatable(DeviceComponentRelatable):
    adapts(Pod)

    group = 'CloudStack'


class ClusterRelatable(DeviceComponentRelatable):
    adapts(Cluster)

    group = 'CloudStack'


class HostRelatable(DeviceComponentRelatable):
    adapts(Host)

    group = 'CloudStack'


### IRelationsProvider Adapters

class CloudRelationsProvider(BaseRelationsProvider):
    adapts(Cloud)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for zone in self._adapted.zones():
                yield self.constructRelationTo(zone, TAG_IMPACTS)


class ZoneRelationsProvider(BaseRelationsProvider):
    adapts(Zone)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for pod in self._adapted.pods():
                yield self.constructRelationTo(pod, TAG_IMPACTS)

        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(self._adapted.cloud())


class PodRelationsProvider(BaseRelationsProvider):
    adapts(Pod)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for cluster in self._adapted.clusters():
                yield self.constructRelationTo(cluster, TAG_IMPACTS)

        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(self._adapted.zone())


class ClusterRelationsProvider(BaseRelationsProvider):
    adapts(Cluster)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTS):
            for host in self._adapted.hosts():
                yield self.constructRelationTo(host, TAG_IMPACTS)

        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(self._adapted.pod())


class HostRelationsProvider(BaseRelationsProvider):
    adapts(Host)

    def relations(self, type=TAG_ALL):
        if type in (TAG_ALL, TAG_IMPACTED_BY):
            yield self.constructRelationTo(self._adapted.cluster())

            device = self._adapted.getManagedDevice()
            if device:
                yield self.constructRelationTo(device, TAG_IMPACTED_BY)
