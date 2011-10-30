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

from Products.ZenRRD.CommandParser import CommandParser

from ZenPacks.zenoss.CloudStack.utils import addLocalLibPath
addLocalLibPath()

import txcloudstack


class CloudStack(CommandParser):
    def processResults(self, cmd, result):
        if 'poll_cloudstack' not in cmd.command:
            return

        data = None
        try:
            data = json.loads(cmd.result.output)
        except Exception, ex:
            result.events.append(dict(
                severity=4,
                summary='error parsing command results',
                message='error parsing command results: %s' % ex,
                eventClassKey='cloudstack_parse_error',
                ))

            return

        # Incorporate events reported by the command.
        for event in data.get('events', []):
            fixed_event = {}
            for k, v in event.items():
                fixed_event[str(k)] = v

            result.events.append(fixed_event)

        metrics = {}

        if 'listhostsresponse' in data:
            metrics.update(
                self._process_listHosts(cmd, data['listhostsresponse']))

        if 'listcapacityresponse' in data:
            for k, v in self._process_listCapacity(
                    cmd, data['listcapacityresponse']).items():

                if k in metrics:
                    metrics[k].update(v)
                else:
                    metrics[k] = v

        if len(metrics.keys()) > 0:
            for point in cmd.points:
                if point.component not in metrics:
                    continue

                if point.id not in metrics[point.component]:
                    continue

                result.values.append((
                    point, metrics[point.component][point.id]))

    def _process_listCapacity(self, cmd, data):
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

        metrics = {'cloud': {}}

        for c in data.get('capacity', []):
            c_type = txcloudstack.capacity_type_string(c['type'])

            for c_key in ('capacitytotal', 'capacityused', 'percentused'):
                metric_name = metric_name_map[(c_type, c_key)]

                # Convert CPU from MHz to Hz.
                if c_type == 'cpu' and not c_key.startswith('percent'):
                    c[c_key] = float(c[c_key]) * 1e6

                # Zone
                if c.get('podid', -1) == -1:
                    metrics['cloud'].setdefault(metric_name, 0)

                    zone_id = 'zone%s' % c['zoneid']
                    metrics.setdefault(zone_id, {})

                    if c_key == 'count':
                        metrics['cloud'][metric_name] += 1
                    else:
                        metrics['cloud'][metric_name] += float(c[c_key])
                        metrics[zone_id][metric_name] = float(c[c_key])

                # Pod
                else:
                    pod_id = 'pod%s' % c['podid']
                    metrics.setdefault(pod_id, {})

                    if c_key != 'count':
                        metrics[pod_id][metric_name] = float(c[c_key])

        # Calculate average percentages for cloud.
        for k, v in metrics['cloud'].items():
            if k.endswith('AllocatedPercent'):
                allocated_k = k.replace('Percent', '')
                total_op_k = k.replace('AllocatedPercent', 'TotalOP')
                metrics['cloud'][k] = (
                    metrics['cloud'][allocated_k] /
                    metrics['cloud'][total_op_k]) * 100.0

            elif k.endswith('UsedPercent'):
                used_k = k.replace('Percent', '')
                total_k = k.replace('UsedPercent', 'Total')
                metrics['cloud'][k] = (
                    metrics['cloud'][used_k] /
                    metrics['cloud'][total_k]) * 100.0

        return metrics

    def _process_listHosts(self, cmd, data):
        metrics = {}

        for h in data.get('host', []):
            if h['type'] != 'Routing':
                continue

            cloud_id = 'cloud'
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

            metrics[host_id] = dict(
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
                if a not in metrics:
                    metrics[a] = {
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

                metrics[a]['cpuTotal'] += cpu_total
                metrics[a]['cpuTotalOP'] += cpu_total_op
                metrics[a]['cpuAllocated'] += cpu_allocated
                metrics[a]['cpuAllocatedPercent'] += cpu_allocated_percent
                metrics[a]['cpuUsed'] += cpu_used
                metrics[a]['cpuUsedPercent'] += cpu_used_percent
                metrics[a]['cpuCores'] += cpu_cores
                metrics[a]['memoryTotal'] += memory_total
                metrics[a]['memoryAllocated'] += memory_allocated
                metrics[a]['memoryAllocatedPercent'] += \
                    memory_allocated_percent

                metrics[a]['memoryUsed'] += memory_used
                metrics[a]['memoryUsedPercent'] += memory_used_percent
                metrics[a]['networkRead'] += network_read
                metrics[a]['networkWrite'] += network_write

        for k, v in metrics.items():
            if k.startswith('zone') or \
                    k.startswith('pod') or \
                    k.startswith('cluster'):

                metrics[k]['cpuAllocatedPercent'] = \
                    (v['cpuAllocated'] / v['cpuTotalOP']) * 100.0

                metrics[k]['cpuUsedPercent'] = \
                    (v['cpuUsed'] / v['cpuTotal']) * 100.0

                metrics[k]['memoryAllocatedPercent'] = \
                    (v['memoryAllocated'] / v['memoryTotal']) * 100.0

                metrics[k]['memoryUsedPercent'] = \
                    (v['memoryUsed'] / v['memoryTotal']) * 100.0

        return metrics
