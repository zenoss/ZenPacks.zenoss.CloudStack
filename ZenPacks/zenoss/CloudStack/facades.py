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

from urlparse import urlparse

from zope.interface import implements

from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.CloudStack.interfaces import ICloudStackFacade


class CloudStackFacade(ZuulFacade):
    implements(ICloudStackFacade)

    def add_cloudstack(self, device_name, url, api_key, secret_key,collector='localhost'):
        """Handles adding a new CloudStack cloud to the system."""

        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(device_name)
        if device:
            return False, _t("A device named %s already exists." % hostname)

        zProperties = {
            'zCloudStackURL': url,
            'zCloudStackAPIKey': api_key,
            'zCloudStackSecretKey': secret_key,
            }

        perfConf = self._dmd.Monitors.getPerformanceMonitor(collector)
        jobStatus = perfConf.addDeviceCreationJob(
            deviceName=device_name,
            devicePath='/Devices/CloudStack',
            performanceMonitor=collector,
            discoverProto='python',
            zProperties=zProperties)

        return True, jobStatus.id
