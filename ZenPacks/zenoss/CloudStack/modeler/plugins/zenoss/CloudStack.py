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
        zone_maps = []

        zones_response = results.get('listzonesresponse', None)
        if zones_response is None:
            LOG.error('No listZones response from API')
            return None

        zones_count = zones_response.get('count', None)
        if zones_count is not None:
            LOG.info('Found %s zones.', zones_count)

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

        zones_map = RelationshipMap(
            relname='zones',
            modname='ZenPacks.zenoss.CloudStack.Zone',
            objmaps=zone_maps)

        return zones_map
