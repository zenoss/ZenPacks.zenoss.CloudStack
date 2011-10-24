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

    def __init__(self):
        self._data = {}

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
        """Combine the results for all API calls into one datastructure."""
        for success, result in results:
            if not success:
                LOG.error("API Error: %s", result.getErrorMessage())
                return None

            data = None

            try:
                data = json.loads(result)
            except Exception, ex:
                LOG.error("Error parsing response: %s", ex)
                LOG.exception(ex)
                return None

            self._data.update(data)

    def process(self, devices, results, unused):
        import pdb; pdb.set_trace()
        return None
