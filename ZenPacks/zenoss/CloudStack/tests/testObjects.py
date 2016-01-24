###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011 TELUS
#
###########################################################################

import re

import logging
log = logging.getLogger('zen.CloudStack')

from zope.component import getUtility

import sys
import os.path

from Products.Five import zcml
from Products.ZenModel.interfaces import IDeviceLoader
from Products.ZenTestCase.BaseTestCase import BaseTestCase


ZENPACK_DEPENDENCIES = (
    'ZenPacks.zenoss.CloudStack',
    )

DEVICECLASS_DEPENDENCIES = tuple()

EVENTCLASS_DEPENDENCIES = (
    '/App',
    '/Capacity',
    '/Perf',
    '/Status',
    )

REPORTCLASS_DEPENDENCIES = tuple()


class TestObjects(BaseTestCase):
    """
    Test suite containing test for objects that should be installed from this
    ZenPack's objects.xml file.

    WARNING: This test suite is slow because its afterSetup loads a lot of
             objects.
    """

    def afterSetUp(self):
        super(TestObjects, self).afterSetUp()

        map(self.dmd.Devices.createOrganizer, (DEVICECLASS_DEPENDENCIES))
        map(self.dmd.Events.createOrganizer, (EVENTCLASS_DEPENDENCIES))
        map(self.dmd.Reports.createOrganizer, (REPORTCLASS_DEPENDENCIES))

        self.dmd.REQUEST = None

        from Products.ZenRelations.ImportRM import NoLoginImportRM
        im = NoLoginImportRM(self.app)

        for zenpack in ZENPACK_DEPENDENCIES:
            __import__(zenpack)
            zp_module = sys.modules[zenpack]

            objects_file = '%s/objects/objects.xml' % zp_module.__path__[0]

            if os.path.isfile(objects_file):
                log.info('Loading objects for %s.', zenpack)
                im.loadObjectFromXML(objects_file)

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import zope.viewlet
        zcml.load_config('meta.zcml', zope.viewlet)

        import ZenPacks.zenoss.CloudStack
        zcml.load_config('configure.zcml', ZenPacks.zenoss.CloudStack)

    def testConfigurationProperties(self):
        """Verify all configuration properties are set properly."""
        dc = self.dmd.Devices.CloudStack
        self.assertEqual(dc.zPingMonitorIgnore, True)
        self.assertEqual(dc.zSnmpMonitorIgnore, True)
        self.assertEqual(dc.zWmiMonitorIgnore, True)
        self.assertEqual(dc.zCollectorPlugins, ['zenoss.CloudStack'])
        self.assertEqual(dc.zDeviceTemplates, ['CloudStackCloud'])
        self.assertEqual(dc.zPythonClass, 'ZenPacks.zenoss.CloudStack.Cloud')
        self.assertEqual(dc.zIcon, '/++resource++cloudstack/img/cloudstack.png')
        self.assertEqual(dc.zCommandCommandTimeout, 300.0)

    def testDeviceLoader(self):
        device_loader = getUtility(IDeviceLoader, 'cloudstack', None)
        job = device_loader().load_device(
            self.dmd, 'x', 'http://cloudstack.example.com/', 'x', 'x')

        self.assertTrue(job)

    def testTemplates(self):
        """Verify all templates are configured properly.

        1. Verify all DERIVE type datapoints have an rrdmin of 0.
        2. Verify all percentage datapoints have rrdmin of 0 and rrdmax of 100.
        """
        template_names = (
            'CloudStackCloud', 'CloudStackZone', 'CloudStackPod',
            'CloudStackCluster', 'CloudStackHost',
            )

        for t_name in template_names:
            t = self.dmd.Devices.CloudStack.rrdTemplates._getOb(t_name)
            for ds in t.datasources():
                for dp in ds.datapoints():
                    if dp.rrdtype == 'DERIVE':
                        self.assertEqual(int(dp.rrdmin), 0)

                    # Lower-bound percentages at 0. No upper-bound to allow for
                    # over-provisioning.
                    elif dp.id.lower().endswith('percent'):
                        self.assertEqual(int(dp.rrdmin), 0)
                        self.assertEqual(dp.rrdmax, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjects))
    return suite
