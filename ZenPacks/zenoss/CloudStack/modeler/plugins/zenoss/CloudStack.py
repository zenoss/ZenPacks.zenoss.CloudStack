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

import json

from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.CloudStack.utils import addLocalLibPath
addLocalLibPath()

import txcloudstack


class CloudStack(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zCloudStackURL',
        'zCloudStackAPIKey',
        'zCloudStackSecretKey',
        )

    def collect(self, device, unused):
        if not device.zCloudStackURL:
            LOG.error('zCloudStackURL is not set. Not discovering')
            return None

        if not device.zCloudStackAPIKey:
            LOG.error('zCloudStackAPIKey is not set. Not discovering.')
            return None

        if not device.zCloudStackSecretKey:
            LOG.error('zCloudStackSecretKey is not set. Not discovering.')
            return None

        client = txcloudstack.Client(
            device.zCloudStackURL,
            device.zCloudStackAPIKey,
            device.zCloudStackSecretKey)

        d = DeferredList((
            client.listZones(),
            client.listPods(),
            client.listClusters(),
            client.listHosts(),
            client.listCapacity(),
            ), consumeErrors=True).addCallback(self._combine)

        return d

    def _combine(self, results):
        all_data = {}

        for success, result in results:
            if not success:
                LOG.error("API Error: %s", result.getErrorMessage())
                return None

            try:
                data = json.loads(result)
            except Exception, ex:
                LOG.error("Error parsing response: %s", ex)
                LOG.exception(ex)
                return None

            all_data.update(data)

        return all_data

    def process(self, device, results, unused):
        maps = []

        for t in ('zones', 'pods', 'clusters', 'hosts'):
            response = results.get('list%sresponse' % t, None)
            if response is None:
                LOG.error('No list%s response from API', t.capitalize())
                return None

            rel_maps = tuple(getattr(self, 'get_%s_rel_maps' % t)(response))

            count = reduce(lambda x, y: x + len(y.maps), rel_maps, 0)
            LOG.info('Found %s %s', count, t)

            maps.extend(rel_maps)

            # No need to process deeper levels if we have no results at this
            # level.
            if count < 1:
                return maps

        return maps

    def get_zones_rel_maps(self, zones_response):
        zone_maps = []
        for zone in zones_response.get('zone', []):
            zone_id = self.prepId(zone['id'])

            zone_maps.append(ObjectMap(data=dict(
                id=zone_id,
                title=zone.get('name', zone_id),
                allocation_state=zone.get('allocationstate', ''),
                guest_cidr_address=zone.get('guestcidraddress', ''),
                dhcp_provider=zone.get('dhcpprovider', ''),
                dns1=zone.get('dns1', ''),
                dns2=zone.get('dns2', ''),
                internal_dns1=zone.get('internaldns1', ''),
                internal_dns2=zone.get('internaldns2', ''),
                network_type=zone.get('networktype', ''),
                security_groups_enabled=zone.get('securitygroupsenabled', ''),
                vlan=zone.get('vlan', ''),
                zone_token=zone.get('zonetoken', ''),
                )))

        yield RelationshipMap(
            relname='zones',
            modname='ZenPacks.zenoss.CloudStack.Zone',
            objmaps=zone_maps)

    def get_pods_rel_maps(self, pods_response):
        pod_maps = {}
        for pod in pods_response.get('pod', []):
            zone_id = self.prepId(pod['zoneid'])
            pod_id = self.prepId(pod['id'])

            compname = 'zones/%s' % zone_id
            pod_maps.setdefault(compname, [])

            pod_maps[compname].append(ObjectMap(data=dict(
                id=pod_id,
                title=pod.get('name', pod_id),
                allocation_state=pod.get('allocationstate', ''),
                start_ip=pod.get('startip', ''),
                end_ip=pod.get('endip', ''),
                netmask=pod.get('netmask', ''),
                gateway=pod.get('gateway', ''),
                )))

        for compname, obj_maps in pod_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='pods',
                modname='ZenPacks.zenoss.CloudStack.Pod',
                objmaps=obj_maps)

    def get_clusters_rel_maps(self, clusters_response):
        cluster_maps = {}
        for cluster in clusters_response.get('cluster', []):
            zone_id = self.prepId(cluster['zoneid'])
            pod_id = self.prepId(cluster['podid'])
            cluster_id = self.prepId(cluster['id'])

            compname = 'zones/%s/pods/%s' % (zone_id, pod_id)
            cluster_maps.setdefault(compname, [])

            cluster_maps[compname].append(ObjectMap(data=dict(
                id=cluster_id,
                title=cluster.get('name', cluster_id),
                allocation_state=cluster.get('allocationstate', ''),
                cluster_type=cluster.get('type', ''),
                hypervisor_type=cluster.get('hypervisor_type', ''),
                managed_state=cluster.get('managedstate', ''),
                )))

        for compname, obj_maps in cluster_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='clusters',
                modname='ZenPacks.zenoss.CloudStack.Cluster',
                objmaps=obj_maps)

    def get_hosts_rel_maps(self, hosts_response):
        host_maps = {}
        for host in hosts_response.get('host', []):
            host_type = host.get('type', None)

            # Only interested in normal hosts which are identified by the
            # Routing type.
            if host_type != 'Routing':
                continue

            zone_id = self.prepId(host['zoneid'])
            pod_id = self.prepId(host['podid'])
            cluster_id = self.prepId(host['clusterid'])
            host_id = self.prepId(host['id'])

            compname = 'zones/%s/pods/%s/clusters/%s' % (
                zone_id, pod_id, cluster_id)

            host_maps.setdefault(compname, [])

            host_maps[compname].append(ObjectMap(data=dict(
                id=host_id,
                title=host.get('name', host_id),
                allocation_state=host.get('allocationstate', ''),
                host_type=host_type,
                host_state=host.get('state', ''),
                host_events=host.get('events', ''),
                host_version=host.get('version', ''),
                hypervisor=host.get('hypervisor', ''),
                capabilities=host.get('capabilities', ''),
                created=host.get('created', ''),
                host_tags=host.get('hosttags', ''),
                ip_address=host.get('ipaddress', ''),
                local_storage_active=host.get('islocalstorageactive', None),
                management_server_id=host.get('managementserverid', None),
                )))

        for compname, obj_maps in host_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='hosts',
                modname='ZenPacks.zenoss.CloudStack.Host',
                objmaps=obj_maps)
