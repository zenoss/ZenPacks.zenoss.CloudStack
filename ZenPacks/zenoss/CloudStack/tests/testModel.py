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
log = logging.getLogger('zen.CloudStack')

from Products.Five import zcml

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.Zuul.interfaces.info import IInfo

from ZenPacks.zenoss.CloudStack.modeler.plugins.zenoss.CloudStack \
        import CloudStack as CloudStackModeler

from ZenPacks.zenoss.CloudStack.tests.utils import loadPickle


CLOUDSTACK_ICON = '/++resource++cloudstack/img/cloudstack.png'


class TestModel(BaseTestCase):
    def afterSetUp(self):
        super(TestModel, self).afterSetUp()

        dc = self.dmd.Devices.createOrganizer('/CloudStack')
        dc.setZenProperty('zPythonClass', 'ZenPacks.zenoss.CloudStack.Cloud')

        self.d = dc.createInstance('zenoss.CloudStack.testDevice')
        self.applyDataMap = ApplyDataMap()._applyDataMap

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import zope.viewlet
        zcml.load_config('meta.zcml', zope.viewlet)

        import ZenPacks.zenoss.CloudStack
        zcml.load_config('configure.zcml', ZenPacks.zenoss.CloudStack)

    def _loadZenossData(self):
        if hasattr(self, '_loaded'):
            return

        modeler = CloudStackModeler()
        modeler_results = loadPickle('cloudstack_results.pickle')

        for data_map in modeler.process(self.d, modeler_results, log):
            self.applyDataMap(self.d, data_map)

        self._loaded = True

    def testCloud(self):
        self._loadZenossData()

        info = IInfo(self.d)
        self.assertEquals(info.zone_count, 1)
        self.assertEquals(info.pod_count, 2)
        self.assertEquals(info.cluster_count, 2)
        self.assertEquals(info.host_count, 6)

    def testZone(self):
        self._loadZenossData()

        zone = self.d.zones._getOb('zone1')
        self.assertEquals(zone.device().id, 'zenoss.CloudStack.testDevice')

        info = IInfo(zone)
        self.assertEquals(info.entity['name'], 'Demo5')
        self.assertEquals(info.icon, CLOUDSTACK_ICON)
        self.assertEquals(info.cloudstack_id, 1)
        self.assertEquals(info.allocation_state, 'Enabled')
        self.assertEquals(info.guest_cidr_address, '10.1.1.0/24')
        self.assertEquals(info.dhcp_provider, 'VirtualRouter')
        self.assertEquals(info.public_dns, '72.52.126.11, ')
        self.assertEquals(info.internal_dns, '72.52.126.12, 72.52.126.12')
        self.assertEquals(info.network_type, 'Advanced')
        self.assertEquals(info.security_groups_enabled, False)
        self.assertEquals(info.vlan, '1000-1200')
        self.assertEquals(info.zone_token, 'f0c6542e-7a1a-39b3-8c92-1a1c67cede0b')
        self.assertEquals(info.pod_count, 2)
        self.assertEquals(info.cluster_count, 2)
        self.assertEquals(info.host_count, 6)

    def testPod(self):
        self._loadZenossData()

        zone = self.d.zones._getOb('zone1')
        pod = zone.pods._getOb('pod1')

        self.assertEquals(pod.device().id, 'zenoss.CloudStack.testDevice')

        info = IInfo(pod)
        self.assertEquals(info.entity['name'], 'Pod-A')
        self.assertEquals(info.icon, CLOUDSTACK_ICON)
        self.assertEquals(info.cloudstack_id, 1)
        self.assertEquals(info.allocation_state, 'Enabled')
        self.assertEquals(info.ip_range, '10.208.37.100 - 10.208.37.120')
        self.assertEquals(info.netmask, '255.255.255.128')
        self.assertEquals(info.gateway, '10.208.37.1')
        self.assertEquals(info.zone.id, 'zone1')
        self.assertEquals(info.cluster_count, 1)
        self.assertEquals(info.host_count, 3)

    def testCluster(self):
        self._loadZenossData()

        zone = self.d.zones._getOb('zone1')
        pod = zone.pods._getOb('pod1')
        cluster = pod.clusters._getOb('cluster1')

        self.assertEquals(cluster.device().id, 'zenoss.CloudStack.testDevice')

        info = IInfo(cluster)
        self.assertEquals(info.entity['name'], 'XenCluster1-D5')
        self.assertEquals(info.icon, CLOUDSTACK_ICON)
        self.assertEquals(info.cloudstack_id, 1)
        self.assertEquals(info.allocation_state, 'Enabled')
        self.assertEquals(info.cluster_type, 'CloudManaged')
        self.assertEquals(info.hypervisor_type, 'XenServer')
        self.assertEquals(info.managed_state, 'Managed')
        self.assertEquals(info.zone.id, 'zone1')
        self.assertEquals(info.pod.id, 'pod1')
        self.assertEquals(info.host_count, 3)

    def testHost(self):
        self._loadZenossData()

        zone = self.d.zones._getOb('zone1')
        pod = zone.pods._getOb('pod1')
        cluster = pod.clusters._getOb('cluster1')
        host = cluster.hosts._getOb('host1')

        self.assertEquals(host.device().id, 'zenoss.CloudStack.testDevice')

        info = IInfo(host)
        self.assertEquals(info.entity['name'], 'demo5-xen')
        self.assertEquals(info.icon, CLOUDSTACK_ICON)
        self.assertEquals(info.cloudstack_id, 1)
        self.assertEquals(info.allocation_state, 'Enabled')
        self.assertEquals(info.host_type, 'Routing')
        self.assertEquals(info.hypervisor, 'XenServer')
        self.assertEquals(info.host_version, '2.2.13.20111117191758')
        self.assertEquals(info.capabilities, 'xen-3.0-x86_64 , xen-3.0-x86_32p , hvm-3.0-x86_32 , hvm-3.0-x86_32p , hvm-3.0-x86_64')
        self.assertEquals(info.host_state, 'Up')
        self.assertEquals(info.created, '2011-10-17T21:19:45-0700')
        self.assertEquals(info.host_tags, '')
        self.assertEquals(info.ip_address, '10.208.37.11')
        self.assertEquals(info.host_events, 'ShutdownRequested; AgentDisconnected; AgentConnected; HypervisorVersionChanged; PrepareUnmanaged; HostDown; PingTimeout; ManagementServerDown; StartAgentRebalance; Ping; MaintenanceRequested')
        self.assertEquals(info.local_storage_active, False)
        self.assertEquals(info.management_server_id, 257544418526661)
        self.assertEquals(info.zone.id, 'zone1')
        self.assertEquals(info.pod.id, 'pod1')
        self.assertEquals(info.cluster.id, 'cluster1')

    def test_getManagedDevice(self):
        self._loadZenossData()

        host_device1 = self.dmd.Devices.createInstance('host_device1')
        host_device1.setManageIp('10.208.37.11')
        host_device1.setPerformanceMonitor('localhost')

        host_device2 = self.dmd.Devices.createInstance('host_device2')
        host_device2.setManageIp('12.34.56.78')
        host_device2.setPerformanceMonitor('localhost')

        from Products.ZenModel.IpInterface import manage_addIpInterface
        manage_addIpInterface(host_device2.os.interfaces, 'eth0', False)
        eth0 = host_device2.os.interfaces._getOb('eth0')
        eth0.setIpAddresses(['10.208.37.12/24'])

        zone = self.d.zones._getOb('zone1')
        pod = zone.pods._getOb('pod1')
        cluster = pod.clusters._getOb('cluster1')

        # Test finding host device by manageIp.
        info1 = IInfo(cluster.hosts._getOb('host1'))
        self.assertEquals(info1.managed_device.id, 'host_device1')

        # Test finding host by interface IP.
        info2 = IInfo(cluster.hosts._getOb('host5'))
        self.assertEquals(info2.managed_device.id, 'host_device2')

    def testMissingHostsResponse(self):
        modeler = CloudStackModeler()
        modeler_results = loadPickle('cloudstack_results_missingHosts.pickle')

        maps = modeler.process(self.d, modeler_results, log)
        self.assertEquals(maps, None)

    def testNoZonesResponse(self):
        modeler = CloudStackModeler()
        modeler_results = loadPickle('cloudstack_results_noZones.pickle')

        maps = modeler.process(self.d, modeler_results, log)
        self.assertEquals(len(maps), 1)
        self.assertEquals(maps[0].relname, 'zones')
        self.assertEquals(len(maps[0].maps), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestModel))
    return suite
