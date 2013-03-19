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

import logging
LOG = logging.getLogger('zen.CloudStack')

from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from ZenPacks.zenoss.CloudStack.utils import add_local_lib_path
add_local_lib_path()

import txcloudstack


class CloudStack(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zCloudStackURL',
        'zCloudStackAPIKey',
        'zCloudStackSecretKey',
        )

    def collect(self, device, unused):
        """Collect model-related information using the txcloudstack library.

        Note: This method is not currently unit tested because we haven't gone
        to the trouble of creating mock results within txcloudstack.
        """
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
            client.listHosts(type="Routing"),
            client.listSystemVms(),
            client.listRouters(),
            client.listVirtualMachines(domainid='1', isrecursive=True),
            client.listCapacity(),
            ), consumeErrors=True).addCallback(self._combine)

        return d

    def _combine(self, results):
        """Combines all responses within results into a single data structure.

        Note: This method is not currently unit tested because we haven't gone
        to the trouble of creating mock results within txcloudstack.
        """
        all_data = {}

        for success, result in results:
            if not success:
                LOG.error("API Error: %s", result.getErrorMessage())
                return None

            all_data.update(result)

        return all_data

    def process(self, device, results, unused):
        maps = []

        response_types = (
            'zones', 'pods', 'clusters', 'hosts', 'systemvms', 'routers',
            'virtualmachines',
            )

        for t in response_types:
            response = results.get('list%sresponse' % t, None)
            if response is None:
                LOG.error('No list%s response from API', t.capitalize())
                return None

            rel_maps = tuple(getattr(self, 'get_%s_rel_maps' % t)(response))

            count = reduce(lambda x, y: x + len(y.maps), rel_maps, 0)
            LOG.info('Found %s %s', count, t)

            maps.extend(rel_maps)

        return maps

    def get_zones_rel_maps(self, zones_response):
        zone_maps = []
        for zone in zones_response.get('zone', []):
            zone_id = self.prepId('zone%s' % zone['id'])

            zone_maps.append(ObjectMap(data=dict(
                id=zone_id,
                title=zone.get('name', zone_id),
                cloudstack_id=zone['id'],
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
            zone_id = self.prepId('zone%s' % pod['zoneid'])
            pod_id = self.prepId('pod%s' % pod['id'])

            compname = 'zones/%s' % zone_id
            pod_maps.setdefault(compname, [])

            pod_maps[compname].append(ObjectMap(data=dict(
                id=pod_id,
                title=pod.get('name', pod_id),
                cloudstack_id=pod['id'],
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
            zone_id = self.prepId('zone%s' % cluster['zoneid'])
            pod_id = self.prepId('pod%s' % cluster['podid'])
            cluster_id = self.prepId('cluster%s' % cluster['id'])

            compname = 'zones/%s/pods/%s' % (zone_id, pod_id)
            cluster_maps.setdefault(compname, [])

            cluster_maps[compname].append(ObjectMap(data=dict(
                id=cluster_id,
                title=cluster.get('name', cluster_id),
                cloudstack_id=cluster['id'],
                allocation_state=cluster.get('allocationstate', ''),
                cluster_type=cluster.get('clustertype', ''),
                hypervisor_type=cluster.get('hypervisortype', ''),
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

            zone_id = self.prepId('zone%s' % host['zoneid'])
            pod_id = self.prepId('pod%s' % host['podid'])
            cluster_id = self.prepId('cluster%s' % host['clusterid'])
            host_id = self.prepId('host%s' % host['id'])

            compname = 'zones/%s/pods/%s/clusters/%s' % (
                zone_id, pod_id, cluster_id)

            host_maps.setdefault(compname, [])

            host_maps[compname].append(ObjectMap(data=dict(
                id=host_id,
                title=host.get('name', host_id),
                cloudstack_id=host['id'],
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

    def get_systemvms_rel_maps(self, systemvms_response):
        systemvm_maps = {}
        for systemvm in systemvms_response.get('systemvm', []):
            zone_id = self.prepId('zone%s' % systemvm['zoneid'])
            pod_id = self.prepId('pod%s' % systemvm['podid'])
            systemvm_id = self.prepId('systemvm%s' % systemvm['id'])

            compname = 'zones/%s/pods/%s' % (zone_id, pod_id)

            systemvm_maps.setdefault(compname, [])

            systemvm_maps[compname].append(ObjectMap(data=dict(
                id=systemvm_id,
                title=systemvm.get('name', systemvm_id),
                cloudstack_id=systemvm['id'],
                gateway=systemvm.get('gateway', ''),
                linklocal_ip=systemvm.get('linklocalip', ''),
                linklocal_macaddress=systemvm.get('linklocalmacaddress', ''),
                linklocal_netmask=systemvm.get('linklocalnetmask', ''),
                network_domain=systemvm.get('networkdomain', ''),
                private_ip=systemvm.get('privateip', ''),
                private_macaddress=systemvm.get('privatemacaddress', ''),
                private_netmask=systemvm.get('privatenetmask', ''),
                public_ip=systemvm.get('publicip', ''),
                public_macaddress=systemvm.get('publicmacaddress', ''),
                public_netmask=systemvm.get('publicnetmask', ''),
                systemvm_type=systemvm.get('systemvmtype', ''),
                template_id=systemvm.get('templateid', None),
                setHostId=systemvm.get('hostid', None),
                )))

        for compname, obj_maps in systemvm_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='systemvms',
                modname='ZenPacks.zenoss.CloudStack.SystemVM',
                objmaps=obj_maps)

    def get_routers_rel_maps(self, routers_response):
        routervm_maps = {}
        for routervm in routers_response.get('router', []):
            zone_id = self.prepId('zone%s' % routervm['zoneid'])
            pod_id = self.prepId('pod%s' % routervm['podid'])
            routervm_id = self.prepId('routervm%s' % routervm['id'])

            compname = 'zones/%s/pods/%s' % (zone_id, pod_id)

            routervm_maps.setdefault(compname, [])

            routervm_maps[compname].append(ObjectMap(data=dict(
                id=routervm_id,
                title=routervm.get('name', routervm_id),
                cloudstack_id=routervm['id'],
                account=routervm.get('account', ''),
                created=routervm.get('created', ''),
                dns1=routervm.get('dns1', ''),
                dns2=routervm.get('dns2', ''),
                domain=routervm.get('domain', ''),
                gateway=routervm.get('gateway', ''),
                guest_ip=routervm.get('guestip', ''),
                guest_macaddress=routervm.get('guestmacaddress', ''),
                guest_netmask=routervm.get('guestnetmask', ''),
                linklocal_ip=routervm.get('linklocalip', ''),
                linklocal_macaddress=routervm.get('linklocalmacaddress', ''),
                linklocal_netmask=routervm.get('linklocalnetmask', ''),
                network_domain=routervm.get('networkdomain', ''),
                public_ip=routervm.get('publicip', ''),
                public_macaddress=routervm.get('publicmacaddress', ''),
                public_netmask=routervm.get('publicnetmask', ''),
                state=routervm.get('state', ''),
                template_id=routervm.get('templateid', None),
                setHostId=routervm.get('hostid', None),
                )))

        for compname, obj_maps in routervm_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='routervms',
                modname='ZenPacks.zenoss.CloudStack.RouterVM',
                objmaps=obj_maps)

    def get_virtualmachines_rel_maps(self, vms_response):
        vm_maps = {}
        for vm in vms_response.get('virtualmachine', []):
            zone_id = self.prepId('zone%s' % vm['zoneid'])
            vm_id = self.prepId('vm%s' % vm['id'])

            compname = 'zones/%s' % zone_id

            vm_maps.setdefault(compname, [])

            memory = None
            if 'memory' in vm:
                memory = vm['memory'] * (1024 ** 2)

            mac_address = ''
            ip_address = ''
            netmask = ''
            gateway = ''

            for nic in vm.get('nic', []):
                if nic.get('isdefault', False):
                    mac_address = nic.get('macaddress', '')
                    ip_address = nic.get('ipaddress', '')
                    netmask = nic.get('netmask', '')
                    gateway = nic.get('gateway', '')

            vm_maps[compname].append(ObjectMap(data=dict(
                id=vm_id,
                title=vm.get('name', vm_id),
                cloudstack_id=vm['id'],
                account=vm.get('account', ''),
                cpu_number=vm.get('cpunumber', None),
                cpu_speed=vm.get('cpuspeed', None),
                created=vm.get('created', ''),
                display_name=vm.get('displayname', ''),
                domain=vm.get('domain', ''),
                ha_enable=vm.get('haenable', False),
                setHostId=vm.get('hostid', None),
                memory=memory,
                mac_address=mac_address,
                ip_address=ip_address,
                netmask=netmask,
                gateway=gateway,
                root_device_type=vm.get('rootdevicetype', ''),
                service_offering=vm.get('serviceofferingname', ''),
                state=vm.get('state', ''),
                template=vm.get('templatename', ''),
                )))

        for compname, obj_maps in vm_maps.items():
            yield RelationshipMap(
                compname=compname,
                relname='vms',
                modname='ZenPacks.zenoss.CloudStack.VirtualMachine',
                objmaps=obj_maps)
