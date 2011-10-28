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

import os.path
import pickle


def loadPickle(filename):
    f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r')
    data = pickle.load(f)
    f.close()
    return data


def mockGetPage(url):
    from twisted.internet import defer

    import re
    match = re.search(r'command=(\w+)', url)
    if not match:
        return defer.fail('No pickle for URL')

    pickle_name = '%sresponse.pickle' % match.group(1).lower()
    return defer.succeed(loadPickle(pickle_name))
