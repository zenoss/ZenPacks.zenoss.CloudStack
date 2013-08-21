##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

'''
Unit test for all-things-Impact.
'''

import transaction

from zope.component import subscribers

from Products.Five import zcml

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenUtils.guid.interfaces import IGUIDManager
from Products.ZenUtils.Utils import monkeypatch

from ZenPacks.zenoss.CloudStack.utils import guid, require_zenpack
from ZenPacks.zenoss.CloudStack.tests.utils import (
    add_contained, add_noncontained,
    )


@monkeypatch('Products.Zuul')
def get_dmd():
    '''
    Retrieve the DMD object. Handle unit test connection oddities.

    This has to be monkeypatched on Products.Zuul instead of
    Products.Zuul.utils because it's already imported into Products.Zuul
    by the time this monkeypatch happens.
    '''
    try:
        # original is injected by the monkeypatch decorator.
        return original()

    except AttributeError:
        connections = transaction.get()._synchronizers.data.values()[:]
        for cxn in connections:
            app = cxn.root()['Application']
            if hasattr(app, 'zport'):
                return app.zport.dmd


def impacts_for(thing):
    '''
    Return a two element tuple.

    First element is a list of object ids impacted by thing. Second element is
    a list of object ids impacting thing.
    '''
    from ZenPacks.zenoss.Impact.impactd.interfaces \
        import IRelationshipDataProvider

    impacted_by = []
    impacting = []

    guid_manager = IGUIDManager(thing.getDmd())
    for subscriber in subscribers([thing], IRelationshipDataProvider):
        for edge in subscriber.getEdges():
            if edge.source == guid(thing):
                impacted_by.append(guid_manager.getObject(edge.impacted).id)
            elif edge.impacted == guid(thing):
                impacting.append(guid_manager.getObject(edge.source).id)

    return (impacted_by, impacting)


def triggers_for(thing):
    '''
    Return a dictionary of triggers for thing.

    Returned dictionary keys will be triggerId of a Trigger instance and
    values will be the corresponding Trigger instance.
    '''
    from ZenPacks.zenoss.Impact.impactd.interfaces import INodeTriggers

    triggers = {}

    for sub in subscribers((thing,), INodeTriggers):
        for trigger in sub.get_triggers():
            triggers[trigger.triggerId] = trigger

    return triggers


def create_cloud(dmd):
    '''
    Return a Cloud suitable for Impact functional testing.
    '''
    # DeviceClass
    dc = dmd.Devices.createOrganizer('/CloudStack')
    dc.setZenProperty('zPythonClass', 'ZenPacks.zenoss.CloudStack.Cloud')

    # Endpoint
    cloud = dc.createInstance('cloud')

    # Zone
    from ZenPacks.zenoss.CloudStack.Zone import Zone
    zone1 = add_contained(cloud, 'zones', Zone('zone1'))

    # Pod
    from ZenPacks.zenoss.CloudStack.Pod import Pod
    pod1 = add_contained(zone1, 'pods', Pod('pod1'))

    # SystemVM
    from ZenPacks.zenoss.CloudStack.SystemVM import SystemVM
    systemvm1 = add_contained(pod1, 'systemvms', SystemVM('systemvm1'))

    # RouterVM
    from ZenPacks.zenoss.CloudStack.RouterVM import RouterVM
    routervm1 = add_contained(pod1, 'routervms', RouterVM('routervm1'))

    # Cluster
    from ZenPacks.zenoss.CloudStack.Cluster import Cluster
    cluster1 = add_contained(pod1, 'clusters', Cluster('cluster1'))

    # Host
    from ZenPacks.zenoss.CloudStack.Host import Host
    host1 = add_contained(cluster1, 'hosts', Host('host1'))
    add_noncontained(host1, 'systemvms', systemvm1)
    add_noncontained(host1, 'routervms', routervm1)

    # VirtualMachine
    from ZenPacks.zenoss.CloudStack.VirtualMachine import VirtualMachine
    vm1 = add_contained(zone1, 'vms', VirtualMachine('vm1'))
    add_noncontained(vm1, 'host', host1)

    return cloud


class TestImpact(BaseTestCase):
    def afterSetUp(self):
        super(TestImpact, self).afterSetUp()

        import Products.ZenEvents
        zcml.load_config('meta.zcml', Products.ZenEvents)

        try:
            import ZenPacks.zenoss.DynamicView
            zcml.load_config('configure.zcml', ZenPacks.zenoss.DynamicView)
        except ImportError:
            return

        try:
            import ZenPacks.zenoss.Impact
            zcml.load_config('meta.zcml', ZenPacks.zenoss.Impact)
            zcml.load_config('configure.zcml', ZenPacks.zenoss.Impact)
        except ImportError:
            return

        import ZenPacks.zenoss.CloudStack
        zcml.load_config('configure.zcml', ZenPacks.zenoss.CloudStack)

    def cloud(self):
        '''
        Return a CloudStack cloud device populated in a suitable way for
        Impact testing.
        '''
        if not hasattr(self, '_cloud'):
            self._cloud = create_cloud(self.dmd)

        return self._cloud

    def assertTriggersExist(self, triggers, expected_trigger_ids):
        '''
        Assert that each expected_trigger_id exists in triggers.
        '''
        for trigger_id in expected_trigger_ids:
            self.assertTrue(
                trigger_id in triggers, 'missing trigger: %s' % trigger_id)

    @require_zenpack('ZenPacks.zenoss.Impact')
    @require_zenpack('ZenPacks.zenoss.XenServer')
    def test_XenServer(self):
        from ZenPacks.zenoss.XenServer.tests.test_impact import create_endpoint
        from ZenPacks.zenoss.XenServer.VM import VM
        from ZenPacks.zenoss.XenServer.VIF import VIF

        xen_endpoint = create_endpoint(self.dmd)
        xen_host = xen_endpoint.getObjByPath('hosts/host1')
        xen_pif = xen_endpoint.getObjByPath('hosts/host1/pifs/pif1')
        xen_pif.ipv4_addresses = ['10.11.12.13']
        xen_pif.index_object()

        xen_vm = xen_endpoint.getObjByPath('vms/vm1')
        xen_vm_vif = xen_endpoint.getObjByPath('vms/vm1/vifs/vif1')
        xen_vm_vif.macaddress = '00:0c:29:fe:ab:bc'
        xen_vm_vif.index_object()

        xen_routervm = add_contained(xen_endpoint, 'vms', VM('xen_routervm1'))
        xen_routervm_vif = add_contained(xen_routervm, 'vifs', VIF('xen_routervm1_vif1'))
        xen_routervm_vif.macaddress = '00:0c:29:fe:ab:bd'
        xen_routervm_vif.index_object()

        xen_systemvm = add_contained(xen_endpoint, 'vms', VM('xen_systemvm1'))
        xen_systemvm_vif = add_contained(xen_systemvm, 'vifs', VIF('xen_systemvm1_vif1'))
        xen_systemvm_vif.macaddress = '00:0c:29:fe:ab:be'
        xen_systemvm_vif.index_object()

        host = self.cloud().getObjByPath('zones/zone1/pods/pod1/clusters/cluster1/hosts/host1')
        host.ip_address = xen_pif.ipv4_addresses[0]
        host.index_object()

        vm = self.cloud().getObjByPath('zones/zone1/vms/vm1')
        vm.mac_address = xen_vm_vif.macaddress
        vm.index_object()

        routervm = self.cloud().getObjByPath('zones/zone1/pods/pod1/routervms/routervm1')
        routervm.linklocal_macaddress = xen_routervm_vif.macaddress
        routervm.index_object()

        systemvm = self.cloud().getObjByPath('zones/zone1/pods/pod1/systemvms/systemvm1')
        systemvm.linklocal_macaddress = xen_systemvm_vif.macaddress
        systemvm.index_object()

        host_impacts, host_impacted_by = impacts_for(host)
        vm_impacts, vm_impacted_by = impacts_for(vm)
        routervm_impacts, routervm_impacted_by = impacts_for(routervm)
        systemvm_impacts, systemvm_impacted_by = impacts_for(systemvm)

        # Host -> CloudStack Host
        self.assertTrue(
            xen_host.id in host_impacted_by,
            'missing impact: {0} -> {1}'.format(xen_host, host))

        # VM -> CloudStack RouterVM
        self.assertTrue(
            xen_vm.id in vm_impacted_by,
            'missing impact: {0} -> {1}'.format(xen_vm, vm))

        # VM -> CloudStack SystemVM
        self.assertTrue(
            xen_routervm.id in routervm_impacted_by,
            'missing impact: {0} -> {1}'.format(xen_routervm, routervm))

        # VM -> CloudStack VirtualMachine
        self.assertTrue(
            xen_systemvm.id in systemvm_impacted_by,
            'missing impact: {0} -> {1}'.format(xen_systemvm, systemvm))
