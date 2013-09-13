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

from twisted.internet import reactor
import twisted.web.client

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.CloudStack.tests.utils import mockGetPage

# Imported or side effect of adding ZenPack's lib directory to sys.path.
import ZenPacks.zenoss.CloudStack.locallibs

# Requires that locallibs first be imported.
import txcloudstack


class TestTXCloudStack(BaseTestCase):
    """Tests for the txcloudstack module.

    No tests are currently implemented in here because there seems to be some
    problem running a reactor in Zope unit tests.
    """

    def afterSetUp(self):
        super(TestTXCloudStack, self).afterSetUp()

        self.client = txcloudstack.Client(
            'http://cloudstack.example.com/', 'x', 'x')

    def test_listConfigurations(self):
        pass

    def test_listZones(self):
        # def _callback(result):
        #     if reactor.running:
        #         reactor.stop()

        #     response = result.get('listzonesresponse', None)
        #     self.assertTrue(isinstance(response, dict))
        #     self.assertEqual(response['count'], 1)
        #     self.assertEqual(len(response['zone']), 1)

        # twisted.web.client.getPage = mockGetPage
        # self.client.listZones().addCallback(_callback)
        # reactor.run()
        pass

    def test_listPods(self):
        pass

    def test_listClusters(self):
        pass

    def test_listHosts(self):
        pass

    def test_listCapacity(self):
        pass

    def test_listAlerts(self):
        pass

    def test_listEvents(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTXCloudStack))
    return suite
