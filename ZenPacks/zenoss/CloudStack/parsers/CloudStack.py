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

        for point in cmd.points:
            if point.component not in metrics:
                continue

            if point.id not in metrics[point.component]:
                continue

            result.values.append((point, metrics[point.component][point.id]))
