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

from Products.Zuul.form import schema
from Products.Zuul.interfaces import IFacade
from Products.Zuul.interfaces import IDeviceInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

# In Zenoss 3 we mistakenly mapped TextLine to Zope's multi-line text
# equivalent and Text to Zope's single-line text equivalent. This was
# backwards so we flipped their meanings in Zenoss 4. The following block of
# code allows the ZenPack to work properly in Zenoss 3 and 4.

# Until backwards compatibility with Zenoss 3 is no longer desired for your
# ZenPack it is recommended that you use "SingleLineText" and "MultiLineText"
# instead of schema.TextLine or schema.Text.
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version

# One of the following branches below will not be covered by unit tests on any
# given Zenoss version because it is a Zenoss version test.
if Version.parse('Zenoss %s' % ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine


class ICloudStackFacade(IFacade):
    def add_cloudstack(self, url, api_key, secret_key):
        """Add CloudStack cloud."""


class ICloudInfo(IDeviceInfo):
    """Interface for Cloud API (Info) adapter."""

    zone_count = schema.Int(title=_t(u"Zone Count"))
    pod_count = schema.Int(title=_t(u"Pod Count"))
    cluster_count = schema.Int(title=_t(u"Cluster Count"))
    host_count = schema.Int(title=_t(u"Host Count"))


class IBaseComponentInfo(IComponentInfo):
    """Abstract base component API (Info) adapter."""

    cloudstack_id = schema.Int(title=_t(u"CloudStack ID"))
    allocation_state = SingleLineText(title=_t(u"Allocation State"))


class IZoneInfo(IBaseComponentInfo):
    """Interface for Zone API (Info) adapter."""

    guest_cidr_address = SingleLineText(title=_t(u"Guest CIDR Address"))
    dhcp_provider = SingleLineText(title=_t(u"DHCP Provider"))
    public_dns = SingleLineText(title=_t(u"Public DNS"))
    internal_dns = SingleLineText(title=_t(u"Internal DNS"))
    network_type = SingleLineText(title=_t(u"Network Type"))
    security_groups_enabled = schema.Bool(title=_t(u"Security Groups Enabled"))
    vlan = SingleLineText(title=_t(u"VLAN Range"))
    zone_token = SingleLineText(title=_t(u"Zone Token"))
    pod_count = schema.Int(title=_t(u"Pod Count"))
    cluster_count = schema.Int(title=_t(u"Cluster Count"))
    host_count = schema.Int(title=_t(u"Host Count"))


class IPodInfo(IBaseComponentInfo):
    """Interface for Pod API (Info) adapter."""

    ip_range = SingleLineText(title=_t(u"IP Range"))
    netmask = SingleLineText(title=_t(u"Netmask"))
    gateway = SingleLineText(title=_t(u"Gateway"))
    zone = schema.Entity(title=_t(u"Zone"))
    cluster_count = schema.Int(title=_t(u"Cluster Count"))
    host_count = schema.Int(title=_t(u"Host Count"))


class IClusterInfo(IBaseComponentInfo):
    """Interface for Cluster API (Info) adapter."""

    cluster_type = SingleLineText(title=_t(u"Cluster Type"))
    hypervisor_type = SingleLineText(title=_t(u"Hypervisor Type"))
    managed_state = SingleLineText(title=_t(u"Managed State"))
    zone = schema.Entity(title=_t(u"Zone"))
    pod = schema.Entity(title=_t(u"Pod"))
    host_count = schema.Int(title=_t(u"Host Count"))


class IHostInfo(IBaseComponentInfo):
    """Interface for Host API (Info) adapter."""

    host_type = SingleLineText(title=_t(u"Host Type"))
    hypervisor = SingleLineText(title=_t(u"Hypervisor"))
    host_version = SingleLineText(title=_t(u"Version"))
    capabilities = SingleLineText(title=_t(u"Capabilities"))
    host_state = SingleLineText(title=_t(u"Host State"))
    created = SingleLineText(title=_t(u"Created"))
    host_tags = SingleLineText(title=_t(u"Host Tags"))
    ip_address = SingleLineText(title=_t(u"IP Address"))
    host_events = SingleLineText(title=_t(u"Event Types"))
    local_storage_active = schema.Bool(title=_t(u"Local Storage Active"))
    management_server_id = schema.Int(title=_t(u"Management Server Identifier"))
    zone = schema.Entity(title=_t(u"Zone"))
    pod = schema.Entity(title=_t(u"Pod"))
    cluster = schema.Entity(title=_t(u"Cluster"))
    host_device = schema.Entity(title=_t(u"Host Device"))
