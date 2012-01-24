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

from Products.ZenTestCase.BaseTestCase import BaseTestCase


class TestAPI(BaseTestCase):
    def afterSetUp(self):
        super(TestAPI, self).afterSetUp()

        # Required to prevent erroring out when trying to define viewlets in
        # ../browser/configure.zcml.
        import zope.viewlet
        zcml.load_config('meta.zcml', zope.viewlet)

        import ZenPacks.zenoss.CloudStack
        zcml.load_config('configure.zcml', ZenPacks.zenoss.CloudStack)

    def testRouterAndFacade(self):
        from ZenPacks.zenoss.CloudStack.routers import CloudStackRouter
        router = CloudStackRouter(self.dmd)

        # Test success case.
        r = router.add_cloudstack('http://cloudstack.example.com/', 'x', 'x')
        self.assertTrue(r.data['success'])
        self.assertTrue(r.data['jobId'].startswith('DeviceCreationJobStatus_'))

        self.dmd.Devices.createInstance('cloudstack.example.com')

        # Test failure case. Device already exists.
        r = router.add_cloudstack('http://cloudstack.example.com/', 'x', 'x')
        self.assertFalse(r.data['success'])
        self.assertEqual(
                r.data['msg'],
                'A device named cloudstack.example.com already exists.')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPI))
    return suite
