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

from zope.interface import implements

from Products.Zuul.decorators import info
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.infos.component import ComponentInfo

from ZenPacks.zenoss.CloudStack.interfaces import (
    ICloudInfo, IZoneInfo, IPodInfo, IClusterInfo, IHostInfo)


class CloudInfo(DeviceInfo):
    """Cloud API (Info) adapter factory."""

    implements(ICloudInfo)

    @property
    def zone_count(self):
        return self._object.zones.countObjects()

    @property
    def pod_count(self):
        return reduce(
            lambda x, y: x + y.pods.countObjects(),
            self._object.zones(),
            0)

    @property
    def cluster_count(self):
        count = 0
        for zone in self._object.zones():
            for pod in zone.pods():
                count += pod.clusters.countObjects()

        return count

    @property
    def host_count(self):
        count = 0
        for zone in self._object.zones():
            for pod in zone.pods():
                for cluster in pod.clusters():
                    count += cluster.hosts.countObjects()

        return count


class BaseComponentInfo(ComponentInfo):
    """Abstract base component API (Info) adapter factory."""

    cloudstack_id = ProxyProperty('cloudstack_id')
    allocation_state = ProxyProperty('allocation_state')

    @property
    def entity(self):
        return {
            'uid': self._object.getPrimaryUrlPath(),
            'name': self._object.titleOrId(),
            }

    @property
    def icon(self):
        return self._object.getIconPath()


class ZoneInfo(BaseComponentInfo):
    """Zone API (Info) adapter factory."""

    implements(IZoneInfo)

    guest_cidr_address = ProxyProperty('guest_cidr_address')
    dhcp_provider = ProxyProperty('dhcp_provider')
    network_type = ProxyProperty('network_type')
    security_groups_enabled = ProxyProperty('security_groups_enabled')
    vlan = ProxyProperty('vlan')
    zone_token = ProxyProperty('zone_token')

    @property
    def public_dns(self):
        return ', '.join((self._object.dns1, self._object.dns2))

    @property
    def internal_dns(self):
        return ', '.join((
            self._object.internal_dns1, self._object.internal_dns1))

    @property
    def pod_count(self):
        return self._object.pods.countObjects()

    @property
    def cluster_count(self):
        return reduce(
            lambda x, y: x + y.clusters.countObjects(),
            self._object.pods(),
            0)

    @property
    def host_count(self):
        count = 0
        for pod in self._object.pods():
            for cluster in pod.clusters():
                count += cluster.hosts.countObjects()

        return count


class PodInfo(BaseComponentInfo):
    """Pod API (Info) adapter factory."""

    implements(IPodInfo)

    netmask = ProxyProperty('netmask')
    gateway = ProxyProperty('gateway')

    @property
    def ip_range(self):
        return "%s - %s" % (self._object.start_ip, self._object.end_ip)

    @property
    @info
    def zone(self):
        return self._object.zone()

    @property
    def cluster_count(self):
        return self._object.clusters.countObjects()

    @property
    def host_count(self):
        return reduce(
            lambda x, y: x + y.hosts.countObjects(),
            self._object.clusters(),
            0)


class ClusterInfo(BaseComponentInfo):
    """Cluster API (Info) adapter factory."""

    implements(IClusterInfo)

    cluster_type = ProxyProperty('cluster_type')
    hypervisor_type = ProxyProperty('hypervisor_type')
    managed_state = ProxyProperty('managed_state')

    @property
    @info
    def zone(self):
        return self._object.pod().zone()

    @property
    @info
    def pod(self):
        return self._object.pod()

    @property
    def host_count(self):
        return self._object.hosts.countObjects()


class HostInfo(BaseComponentInfo):
    """Host API (Info) adapter factory."""

    implements(IHostInfo)

    host_type = ProxyProperty('host_type')
    hypervisor = ProxyProperty('hypervisor')
    host_version = ProxyProperty('host_version')
    capabilities = ProxyProperty('capabilities')
    host_state = ProxyProperty('host_state')
    created = ProxyProperty('created')
    host_tags = ProxyProperty('host_tags')
    ip_address = ProxyProperty('ip_address')
    host_events = ProxyProperty('host_events')
    local_storage_active = ProxyProperty('local_storage_active')
    management_server_id = ProxyProperty('management_server_id')

    @property
    @info
    def zone(self):
        return self._object.cluster().pod().zone()

    @property
    @info
    def pod(self):
        return self._object.cluster().pod()

    @property
    @info
    def cluster(self):
        return self._object.cluster()
