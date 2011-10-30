#!/usr/bin/env python
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

import json
import md5
import os
import sys
import tempfile
import time

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from utils import addLocalLibPath
addLocalLibPath()

import txcloudstack


class CloudStackPoller(object):
    def __init__(self, url, api_key, secret_key):
        self._url = url
        self._api_key = api_key
        self._secret_key = secret_key

    def _temp_filename(self):
        target_hash = md5.md5('%s+%s+%s' % (
            self._url, self._api_key, self._secret_key)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_cloudstack_metrics_%s' % target_hash)

    def _cache_results(self, data):
        tmpfile = self._temp_filename()
        tmp = open(tmpfile, 'w')
        json.dump(data, tmp)
        tmp.close()

    def _cached_results(self):
        tmpfile = self._temp_filename()
        if not os.path.isfile(tmpfile):
            return None

        # Make sure temporary data isn't too stale.
        if os.stat(tmpfile).st_mtime < (time.time() - 50):
            os.unlink(tmpfile)
            return None

        tmp = open(tmpfile, 'r')
        data = json.load(tmp)
        tmp.close()

        return data

    def run(self):
        def callback(results):
            if reactor.running:
                reactor.stop()

            data = {'events': []}

            for success, result in results:
                if not success:
                    error = result.getErrorMessage()
                    data['events'].append(dict(
                        severity=4,
                        summary='CloudStack error: %s' % error,
                        eventClassKey='cloudstack_error',
                        ))

                    print json.dumps(data)
                    return

                try:
                    data.update(json.loads(result))
                except Exception, ex:
                    data['events'].append(dict(
                        severity=4,
                        summary='error parsing API response',
                        message='error parsing API response: %s' % ex,
                        eventClassKey='cloudstack_parse_error',
                        ))

                    print json.dumps(data)
                    return

            self._cache_results(results)

            data['events'].append(dict(
                severity=0,
                summary='CloudStack polled successfully',
                eventKey='cloudstackFailure',
                eventClassKey='cloudstack_success',
                ))

            print json.dumps(data)

        cached_results = self._cached_results()
        if cached_results is not None:
            callback(cached_results)
            return

        client = txcloudstack.Client(
            self._url,
            self._api_key,
            self._secret_key)

        DeferredList((
            client.listCapacity(),
            client.listHosts(type="Routing"),
            ), consumeErrors=True).addCallback(callback)

        reactor.run()


if __name__ == '__main__':
    usage = "Usage: %s <url> <apikey> <secretkey>"

    url = api_key = secret_key = None
    try:
        url, api_key, secret_key = sys.argv[1:4]
    except ValueError:
        print >> sys.stderr, usage % sys.argv[0]
        sys.exit(1)

    poller = CloudStackPoller(url, api_key, secret_key)
    poller.run()
