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


def stringify_keys(dictionary):
    """Convert all keys of given dictionary to strings."""
    fixed_dictionary = {}
    for k, v in dictionary.items():
        fixed_dictionary[str(k)] = v

    return fixed_dictionary


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
                eventKey='cloudstack_failure',
                eventClassKey='cloudstack_parse_error',
                ))

            return

        # Pass incoming events straight through.
        result.events.extend(map(stringify_keys, data.get('events', [])))

        # Map incoming values to their components and datapoints.
        if len(data.get('values', {}).keys()) > 0:
            for point in cmd.points:
                if point.component not in data['values']:
                    continue

                if point.id not in data['values'][point.component]:
                    continue

                result.values.append((
                    point, data['values'][point.component][point.id]))

        return result
