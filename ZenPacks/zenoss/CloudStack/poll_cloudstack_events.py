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

from utils import add_local_lib_path
add_local_lib_path()

import txcloudstack


def zenoss_severity(level):
    return {
        'INFO': 2,
        'WARN': 3,
        'ERROR': 4,
        }.get(level, 3)


class CloudStackPoller(object):
    def __init__(self, url, api_key, secret_key):
        self._url = url
        self._api_key = api_key
        self._secret_key = secret_key
        self._load_last()

    def _temp_filename(self):
        target_hash = md5.md5('%s+%s+%s' % (
            self._url, self._api_key, self._secret_key)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_cloudstack_events_%s' % target_hash)

    def _load_last(self):
        tmpfile = self._temp_filename()
        if not os.path.isfile(tmpfile):
            self._last_alert_sent = None
            self._last_alert_id = None
            self._last_event_sent = None
            self._last_event_id = None
        else:
            tmp = open(tmpfile, 'r')
            data = json.load(tmp)
            tmp.close()
            self._last_alert_sent = data['last_alert_sent']
            self._last_alert_id = data['last_alert_id']
            self._last_event_sent = data['last_event_sent']
            self._last_event_id = data['last_event_id']

    def _save_last(self):
        tmpfile = self._temp_filename()
        tmp = open(tmpfile, 'w')
        json.dump({
            'last_alert_sent': self._last_alert_sent,
            'last_alert_id': self._last_alert_id,
            'last_event_sent': self._last_event_sent,
            'last_event_id': self._last_event_id,
            }, tmp)

        tmp.close()

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
                        eventKey='cloudstack_failure',
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
                        eventKey='cloudstack_failure',
                        eventClassKey='cloudstack_parse_error',
                        ))

                    print json.dumps(data)
                    return

            if 'listalertsresponse' in data:
                for alert in data['listalertsresponse'].get('alert', []):
                    data['events'].append(dict(
                        severity=3,
                        summary=alert['description'],
                        eventClassKey='cloudstack_alert_%s' % alert['type'],
                        rcvtime=alert['sent'],
                        ))

                del(data['listalertsresponse'])

            if 'listeventsresponse' in data:
                for event in data['listeventsresponse'].get('event', []):
                    data['events'].append(dict(
                        severity=zenoss_severity(event['level']),
                        summary=event['description'],
                        eventClassKey='cloudstack_event_%s' % event['type'],
                        rcvtime=event['created'],
                        ))

                del(data['listeventsresponse'])

            self._save_last()

            data['events'].append(dict(
                severity=0,
                summary='CloudStack polled successfully',
                eventKey='cloudstackFailure',
                eventClassKey='cloudstack_success',
                ))

            print json.dumps(data)

        client = txcloudstack.Client(
            self._url,
            self._api_key,
            self._secret_key)

        DeferredList((
            client.listAlerts(),
            client.listEvents(),
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
