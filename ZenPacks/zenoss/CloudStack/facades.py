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
from zope.event import notify
from ZODB.transact import transact

from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.CloudStack.interfaces import ICloudStackFacade


class CloudStackFacade(ZuulFacade):
    implements(ICloudStackFacade)

    def add_cloudstack(self, device_name, url, api_key, secret_key, collector='localhost'):
        """Handles adding a new CloudStack cloud to the system."""

        @transact
        def create_device():
            dc = self._dmd.Devices.getOrganizer('/Devices/CloudStack')

            account = dc.createInstance(device_name)
            account.setPerformanceMonitor(collector)
            account.setZenProperty('zCloudStackURL', url)
            account.setZenProperty('zCloudStackAPIKey', api_key)
            account.setZenProperty('zCloudStackSecretKey', secret_key)

            account.index_object()
            notify(IndexingEvent(account))


        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(device_name)
        if device:
            return False, _t("A device named %s already exists." % device_name)

        # This must be committed before the following model can be
        # scheduled.
        create_device()

        # Schedule a modeling job for the new account.
        account = deviceRoot.findDeviceByIdExact(device_name)
        account.collectDevice(setlog=False, background=True)

        return True
