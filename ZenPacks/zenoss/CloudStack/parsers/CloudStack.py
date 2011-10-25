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

from Products.ZenRRD.CommandParser import CommandParser


class CloudStack(CommandParser):
    def processResults(self, cmd, result):
        if 'poll_cloudstack' not in cmd.command:
            return

        import pdb; pdb.set_trace()
        pass
