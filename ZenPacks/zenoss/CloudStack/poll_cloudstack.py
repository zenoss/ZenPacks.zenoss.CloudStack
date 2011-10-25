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

from utils import addLocalLibPath
addLocalLibPath()

import txcloudstack


class CloudStackPoller(object):
    def __init__(self, url, api_key, secret_key):
        self._url = url
        self._api_key = api_key
        self._secret_key = secret_key

    def _getTempFilename(self):
        target_hash = md5.md5('%s+%s+%s' % (
            self._url, self._api_key, self._secret_key)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_cloudstack_%s' % target_hash)

    def _cacheData(self, data):
        tmpfile = self._getTempFilename()
        tmp = open(tmpfile, 'w')
        json.dump(data, tmp)
        tmp.close()

    def _loadData(self):
        tmpfile = self._getTempFilename()
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
        def callback(result):
            data = {'events': []}

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

            self._cacheData(result)

            data['events'].append(dict(
                severity=0,
                summary='CloudStack polled successfully',
                eventKey='cloudstackFailure',
                eventClassKey='cloudstack_success',
                ))

            print json.dumps(data)

        def errback(error):
            data = {'events': []}
            data['events'].append(dict(
                severity=4,
                summary='CloudStack error: %s' % error.getErrorMessage(),
                eventClassKey='cloudstack_error',
                ))

            print json.dumps(data)

        last_result = self._loadData()
        if last_result is not None:
            callback(last_result)
            return

        client = txcloudstack.Client(
            self._url,
            self._api_key,
            self._secret_key)

        client.listCapacity().addCallbacks(
            callback=callback,
            errback=errback).addBoth(lambda x: reactor.stop())

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
