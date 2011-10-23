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

import base64
import hashlib
import hmac
import json
import urllib

from twisted.internet.defer import DeferredList
from twisted.web.client import getPage


# http://cloudstack.org/forum/6-general-discussion/7102-performance-monitoring-option-for-cloudcom.html
CAPACITY_TYPE = {
    0: 'memory',  # bytes
    1: 'cpu',  # MHz
    2: 'primary_storage_used',  # bytes
    3: 'primary_storage_allocated',  # bytes
    4: 'public_ips',
    5: 'private_ips',
    6: 'secondary_storage',  # bytes
    }


class Client(object):
    """CloudStack client."""

    def __init__(self, base_url, api_key, secret_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.secret_key = secret_key
        self._page_size = None

    def _sign(self, url):
        """Generate a signed URL for the provided url and secret key.

        The procedure for creating a signature is documented at
        http://docs.cloud.com/CloudStack_Documentation/Developer's_Guide%3A_CloudStack
        """

        base_url, query_string = url.split('?')
        msg = '&'.join(sorted(x.lower() for x in query_string.split('&')))

        signature = base64.b64encode(hmac.new(
            self.secret_key, msg=msg, digestmod=hashlib.sha1).digest())

        return '%s?%s&signature=%s' % (
            base_url, query_string, urllib.quote(signature))

    def _request(self, command, **kwargs):
        params = kwargs
        params['command'] = command
        params['apiKey'] = self.api_key
        params['response'] = 'json'

        url = self._sign("%s/client/api?%s" % (
            self.base_url, urllib.urlencode(params)))

        return getPage(url)

    def listZones(self):
        return self._request('listZones')

    def listPods(self):
        return self._request('listPods')

    def listClusters(self):
        return self._request('listClusters')

    def listHosts(self):
        return self._request('listHosts')

    def listCapacity(self):
        return self._request('listCapacity')


if __name__ == '__main__':
    import os

    from twisted.internet import reactor

    client = Client(
        os.environ.get('CLOUDSTACK_URL', 'http://localhost/'),
        os.environ.get('CLOUDSTACK_APIKEY', 'asd123'),
        os.environ.get('CLOUDSTACK_SECRETKEY', 'asd123'))

    def callback(results):
        reactor.stop()

        for success, result in results:
            if success:
                data = json.loads(result)
                if 'listcapacityresponse' in data:
                    for c in data['listcapacityresponse']['capacity']:
                        if 'podname' not in c:
                            c['podname'] = 'x'
                            pass

                        print "%s - z:%s p:%s - total:%s" % (
                            CAPACITY_TYPE[c['type']],
                            c['zonename'], c['podname'],
                            c['capacitytotal'])
                else:
                    from pprint import pprint
                    pprint(data)
                    pass
            else:
                print result.getErrorMessage()

    DeferredList((
        client.listZones(),
        client.listPods(),
        client.listClusters(),
        client.listHosts(),
        client.listCapacity(),
        ), consumeErrors=True).addCallback(callback)

    reactor.run()
