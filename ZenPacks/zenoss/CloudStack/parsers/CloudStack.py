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
        result.events.extend(data.get('events', []))

        metrics = self._process_listCapacity(cmd, data)
        metrics.update(self._process_listHosts(cmd, data))

        for point in cmd.points:
            if point.component not in metrics:
                continue

            if point.id not in metrics[point.component]:
                continue

            result.values.append((point, metrics[point.component][point.id]))

    def _process_listCapacity(self, cmd, data):
        prefix_map = {
            'memory': 'memory',
            'cpu': 'cpu',
            'primary_storage_used': 'primaryStorage',
            'primary_storage_allocated': 'primaryStorageAlloc',
            'public_ips': 'publicIPs',
            'private_ips': 'privateIPs',
            'secondary_storage': 'secondaryStorage',
            }

        suffix_map = {
            'capacitytotal': 'Total',
            'capacityused': 'Used',
            'percentused': 'Percent',
            'count': 'Count',
            }

        metrics = {'cloud': {}}

        for c in data.get('listcapacityresponse', {}).get('capacity', []):
            c_type = txcloudstack.capacity_type_string(c['type'])
            prefix = prefix_map[c_type]

            for c_key, suffix in suffix_map.items():
                metric_name = '%s%s' % (prefix, suffix)

                # Convert CPU from MHz to Hz.
                if prefix == 'cpu' and suffix in ('Total', 'Used'):
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
        for prefix in prefix_map.values():
            percent_key = '%sPercent' % prefix
            count_key = '%sCount' % prefix
            if percent_key in metrics['cloud']:
                metrics['cloud'][percent_key] = \
                    metrics['cloud'][percent_key] / metrics['cloud'][count_key]

        return metrics

    def _process_listHosts(self, cmd, data):
        def init_cluster():
            return {
                'cpuTotal': 0,
                'cpuTotalOP': 0,
                'cpuAllocated': 0,
                'cpuAllocatedPercent': 0,
                'cpuUsed': 0,
                'cpuUsedPercent': 0,
                'cpuCores': 0,
                'memoryTotal': 0,
                'memoryAllocated': 0,
                'memoryAllocatedPercent': 0,
                'memoryUsed': 0,
                'memoryUsedPercent': 0,
                'networkRead': 0,
                'networkWrite': 0,
                }

        metrics = {}

        for h in data.get('listhostsresponse', {}).get('host', []):
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

            network_read = float(h['networkkbsread']) * 1024
            network_write = float(h['networkkbswrite']) * 1024

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

            if cluster_id not in metrics:
                metrics[cluster_id] = init_cluster()

            metrics[cluster_id]['cpuTotal'] += cpu_total
            metrics[cluster_id]['cpuTotalOP'] += cpu_total_op
            metrics[cluster_id]['cpuAllocated'] += cpu_allocated
            metrics[cluster_id]['cpuAllocatedPercent'] += cpu_allocated_percent
            metrics[cluster_id]['cpuUsed'] += cpu_used
            metrics[cluster_id]['cpuUsedPercent'] += cpu_used_percent
            metrics[cluster_id]['cpuCores'] += cpu_cores
            metrics[cluster_id]['memoryTotal'] += memory_total
            metrics[cluster_id]['memoryAllocated'] += memory_allocated
            metrics[cluster_id]['memoryAllocatedPercent'] += \
                memory_allocated_percent

            metrics[cluster_id]['memoryUsed'] += memory_used
            metrics[cluster_id]['memoryUsedPercent'] += memory_used_percent
            metrics[cluster_id]['networkRead'] += network_read
            metrics[cluster_id]['networkWrite'] += network_write

        for k, v in metrics.items():
            if k.startswith('cluster'):
                metrics[k]['cpuAllocatedPercent'] = \
                    (v['cpuAllocated'] / v['cpuTotalOP']) * 100.0

                metrics[k]['cpuUsedPercent'] = \
                    (v['cpuUsed'] / v['cpuTotal']) * 100.0

                metrics[k]['memoryAllocatedPercent'] = \
                    (v['memoryAllocated'] / v['memoryTotal']) * 100.0

                metrics[k]['memoryUsedPercent'] = \
                    (v['memoryUsed'] / v['memoryTotal']) * 100.0

        return metrics
