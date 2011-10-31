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

import xml.utils.iso8601

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from utils import add_local_lib_path
add_local_lib_path()

import txcloudstack

SEVERITY_MAP = {
    'INFO': 2,
    'WARN': 3,
    'ERROR': 4,
    }


class CloudStackPoller(object):
    def __init__(self, url, api_key, secret_key, collect_events=False):
        self._url = url
        self._api_key = api_key
        self._secret_key = secret_key
        self._collect_events = collect_events
        self._events = []
        self._values = {}

    def _temp_filename(self, key):
        target_hash = md5.md5('%s+%s+%s' % (
            self._url, self._api_key, self._secret_key)).hexdigest()

        return os.path.join(
            tempfile.gettempdir(),
            '.zenoss_cloudstack_%s_%s' % (key, target_hash))

    def _cache_values(self, values):
        tmpfile = self._temp_filename(key='values')
        tmp = open(tmpfile, 'w')
        json.dump(values, tmp)
        tmp.close()

    def _cached_values(self):
        tmpfile = self._temp_filename(key='values')
        if not os.path.isfile(tmpfile):
            return None

        # Make sure temporary data isn't too stale.
        if os.stat(tmpfile).st_mtime < (time.time() - 50):
            os.unlink(tmpfile)
            return None

        tmp = open(tmpfile, 'r')
        values = json.load(tmp)
        tmp.close()

        return values

    def _print_output(self):
        print json.dumps({'events': self._events, 'values': self._values})

    def _process_listAlerts(self, response):
        events = []

        for alert in response.get('alert', []):
            rcvtime = xml.utils.iso8601.parse(alert['sent'])
            events.append(dict(
                severity=3,
                summary=alert['description'],
                eventClassKey='cloudstack_alert_%s' % alert['type'],
                rcvtime=rcvtime,
                ))

        return events

    def _process_listEvents(self, response):
        events = []

        for event in response.get('event', []):
            rcvtime = xml.utils.iso8601.parse(event['created'])
            events.append(dict(
                severity=SEVERITY_MAP.get(event['level'], 3),
                summary=event['description'],
                eventClassKey='cloudstack_event_%s' % event['type'],
                rcvtime=rcvtime,
                ))

        return events

    def _process_listHosts(self, response):
        values = {}

        cloud_id = 'cloud'

        for h in response.get('host', []):
            if h['type'] != 'Routing':
                continue

            zone_id = 'zone%s' % h['zoneid']
            pod_id = 'pod%s' % h['podid']
            cluster_id = 'cluster%s' % h['clusterid']
            host_id = 'host%s' % h['id']

            # Massage the host capacity data into the metrics we want.
            cpu_cores = h['cpunumber']
            cpu_total = cpu_cores * h['cpuspeed'] * 1e6
            cpu_total_op = float(h['cpuwithoverprovisioning']) * 1e6
            cpu_allocated_percent = float(h['cpuallocated'].rstrip('%'))
            cpu_allocated = cpu_total_op * (cpu_allocated_percent * 0.01)
            cpu_used_percent = float(h['cpuused'].rstrip('%'))
            cpu_used = cpu_total * (cpu_used_percent * 0.01)

            memory_total = float(h['memorytotal'])
            memory_allocated = float(h['memoryallocated'])
            memory_allocated_percent = (memory_allocated / memory_total) * 100.0
            memory_used = float(h['memoryused'])
            memory_used_percent = (memory_used / memory_total) * 100.0

            # Convert networkkbs* to bits/sec.
            network_read = float(h['networkkbsread']) * 1024 * 8
            network_write = float(h['networkkbswrite']) * 1024 * 8

            values[host_id] = dict(
                cpuTotal=cpu_total,
                cpuTotalOP=cpu_total_op,
                cpuAllocated=cpu_allocated,
                cpuAllocatedPercent=cpu_allocated_percent,
                cpuUsed=cpu_used,
                cpuUsedPercent=cpu_used_percent,
                cpuCores=cpu_cores,
                memoryTotal=memory_total,
                memoryAllocated=memory_allocated,
                memoryAllocatedPercent=memory_allocated_percent,
                memoryUsed=memory_used,
                memoryUsedPercent=memory_used_percent,
                networkRead=network_read,
                networkWrite=network_write,
                )

            for a in (cloud_id, zone_id, pod_id, cluster_id):
                if a not in values:
                    values[a] = {
                        'memoryTotal': 0,
                        'memoryAllocated': 0,
                        'memoryAllocatedPercent': 0,
                        'memoryUsed': 0,
                        'memoryUsedPercent': 0,
                        'cpuTotalOP': 0,
                        'cpuTotal': 0,
                        'cpuAllocated': 0,
                        'cpuAllocatedPercent': 0,
                        'cpuUsed': 0,
                        'cpuUsedPercent': 0,
                        'cpuCores': 0,
                        'networkRead': 0,
                        'networkWrite': 0,
                        }

                values[a]['cpuTotal'] += cpu_total
                values[a]['cpuTotalOP'] += cpu_total_op
                values[a]['cpuAllocated'] += cpu_allocated
                values[a]['cpuAllocatedPercent'] += cpu_allocated_percent
                values[a]['cpuUsed'] += cpu_used
                values[a]['cpuUsedPercent'] += cpu_used_percent
                values[a]['cpuCores'] += cpu_cores
                values[a]['memoryTotal'] += memory_total
                values[a]['memoryAllocated'] += memory_allocated
                values[a]['memoryAllocatedPercent'] += memory_allocated_percent
                values[a]['memoryUsed'] += memory_used
                values[a]['memoryUsedPercent'] += memory_used_percent
                values[a]['networkRead'] += network_read
                values[a]['networkWrite'] += network_write

        for k, v in values.items():
            if k.startswith('zone') or \
                    k.startswith('pod') or \
                    k.startswith('cluster'):

                values[k]['cpuAllocatedPercent'] = \
                    (v['cpuAllocated'] / v['cpuTotalOP']) * 100.0

                values[k]['cpuUsedPercent'] = \
                    (v['cpuUsed'] / v['cpuTotal']) * 100.0

                values[k]['memoryAllocatedPercent'] = \
                    (v['memoryAllocated'] / v['memoryTotal']) * 100.0

                values[k]['memoryUsedPercent'] = \
                    (v['memoryUsed'] / v['memoryTotal']) * 100.0

        return values

    def _process_listCapacity(self, response):
        values = {'cloud': {}}

        metric_name_map = {
            ('public_ips', 'capacitytotal'): 'publicIPsTotal',
            ('public_ips', 'capacityused'): 'publicIPsUsed',
            ('public_ips', 'percentused'): 'publicIPsUsedPercent',
            ('private_ips', 'capacitytotal'): 'privateIPsTotal',
            ('private_ips', 'capacityused'): 'privateIPsUsed',
            ('private_ips', 'percentused'): 'privateIPsUsedPercent',
            ('memory', 'capacitytotal'): 'memoryTotalOP',
            ('memory', 'capacityused'): 'memoryAllocated',
            ('memory', 'percentused'): 'memoryAllocatedPercent',
            ('cpu', 'capacitytotal'): 'cpuTotalOP',
            ('cpu', 'capacityused'): 'cpuAllocated',
            ('cpu', 'percentused'): 'cpuAllocatedPercent',
            ('primary_storage_allocated', 'capacitytotal'): 'primaryStorageTotalOP',
            ('primary_storage_allocated', 'capacityused'): 'primaryStorageAllocated',
            ('primary_storage_allocated', 'percentused'): 'primaryStorageAllocatedPercent',
            ('primary_storage_used', 'capacitytotal'): 'primaryStorageTotal',
            ('primary_storage_used', 'capacityused'): 'primaryStorageUsed',
            ('primary_storage_used', 'percentused'): 'primaryStorageUsedPercent',
            ('secondary_storage', 'capacitytotal'): 'secondaryStorageTotal',
            ('secondary_storage', 'capacityused'): 'secondaryStorageUsed',
            ('secondary_storage', 'percentused'): 'secondaryStorageUsedPercent',
        }

        for c in response.get('capacity', []):
            c_type = txcloudstack.capacity_type_string(c['type'])

            for c_key in ('capacitytotal', 'capacityused', 'percentused'):
                metric_name = metric_name_map[(c_type, c_key)]

                # Convert CPU from MHz to Hz.
                if c_type == 'cpu' and not c_key.startswith('percent'):
                    c[c_key] = float(c[c_key]) * 1e6

                # Zone
                if c.get('podid', -1) == -1:
                    values['cloud'].setdefault(metric_name, 0)

                    zone_id = 'zone%s' % c['zoneid']
                    values.setdefault(zone_id, {})

                    values['cloud'][metric_name] += float(c[c_key])
                    values[zone_id][metric_name] = float(c[c_key])

                # Pod
                else:
                    pod_id = 'pod%s' % c['podid']
                    values.setdefault(pod_id, {})

                    values[pod_id][metric_name] = float(c[c_key])

        # Calculate average percentages for cloud.
        for k, v in values['cloud'].items():
            if k.endswith('AllocatedPercent'):
                allocated_k = k.replace('Percent', '')
                total_op_k = k.replace('AllocatedPercent', 'TotalOP')
                values['cloud'][k] = (
                    values['cloud'][allocated_k] /
                    values['cloud'][total_op_k]) * 100.0

            elif k.endswith('UsedPercent'):
                used_k = k.replace('Percent', '')
                total_k = k.replace('UsedPercent', 'Total')
                values['cloud'][k] = (
                    values['cloud'][used_k] /
                    values['cloud'][total_k]) * 100.0

        return values

    def _callback(self, results):
        if reactor.running:
            reactor.stop()

        data = {}

        for success, result in results:
            if not success:
                error = result.getErrorMessage()
                self._events.append(dict(
                    severity=4,
                    summary='CloudStack error: %s' % error,
                    eventKey='cloudstack_failure',
                    eventClassKey='cloudstack_error',
                    ))

                self._print_output()
                return

            try:
                data.update(json.loads(result))
            except Exception, ex:
                self._events.append(dict(
                    severity=4,
                    summary='error parsing API response',
                    message='error parsing API response: %s' % ex,
                    eventKey='cloudstack_failure',
                    eventClassKey='cloudstack_parse_error',
                    ))

                self._print_output()
                return

        if 'listalertsresponse' in data:
            self._events.extend(
                self._process_listAlerts(data['listalertsresponse']))

        if 'listeventsresponse' in data:
            self._events.extend(
                self._process_listEvents(data['listeventsresponse']))

        if 'listhostsresponse' in data:
            self._values.update(
                self._process_listHosts(data['listhostsresponse']))

        if 'listcapacityresponse' in data:
            capacity = self._process_listCapacity(data['listcapacityresponse'])
            for component, values in capacity.items():
                for k, v in values.items():
                    if component in self._values:
                        self._values[component].update(values)
                    else:
                        self._values[component] = values

        self._events.append(dict(
            severity=0,
            summary='CloudStack polled successfully',
            eventKey='cloudstack_failure',
            eventClassKey='cloudstack_success',
            ))

        self._print_output()

    def run(self):
        client = txcloudstack.Client(
            self._url,
            self._api_key,
            self._secret_key)

        deferreds = []

        if self._collect_events:
            deferreds.extend((
                client.listAlerts(),
                client.listEvents(),
                ))
        else:
            cached_values = self._cached_values()
            if cached_values is not None:
                self._values = cached_values
                self._print_output()
                return

            deferreds.extend((
                client.listCapacity(),
                client.listHosts(type="Routing"),
                ))

        DeferredList(deferreds, consumeErrors=True).addCallback(self._callback)

        reactor.run()


if __name__ == '__main__':
    usage = "Usage: %s <url> <apikey> <secretkey>"

    url = api_key = secret_key = None
    try:
        url, api_key, secret_key = sys.argv[1:4]
    except ValueError:
        print >> sys.stderr, usage % sys.argv[0]
        sys.exit(1)

    events = False
    if len(sys.argv) > 4 and sys.argv[4] == 'events':
        events = True

    poller = CloudStackPoller(url, api_key, secret_key, collect_events=events)
    poller.run()
