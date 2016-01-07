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

from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne


LOCAL_RELNAMES = {
    'zones',
    }

# Guard against conflicting relationships being introduced. (ZEN-12144)
BASE_RELATIONS = tuple(
    x for x in Device._relations if x[0] not in LOCAL_RELNAMES)


class Cloud(Device):
    meta_type = portal_type = "CloudStackCloud"

    _relations = BASE_RELATIONS + (
        ('zones', ToManyCont(ToOne,
            'ZenPacks.zenoss.CloudStack.Zone.Zone',
            'cloud')
            ),
        )


    def isRootAdmin(self):
        # only root admin has Pod component
        pods = self.getDeviceComponents(type='CloudStackPod')
        return len(pods) > 0


    def getRRDTemplates(self):
        templates = super(Cloud, self).getRRDTemplates()
        if not self.isRootAdmin():
            return []

        return templates
