##############################################################################
#
# Copyright (C) Zenoss, Inc. 2011, 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import os.path
import pickle
import re

from twisted.internet import defer


def loadString(filename):
    f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r')
    data = f.read()
    f.close()
    return data


def loadPickle(filename):
    f = open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r')
    data = pickle.load(f)
    f.close()
    return data


def mockGetPage(url):
    match = re.search(r'command=(\w+)', url)
    if not match:
        return defer.fail('No JSON for URL')

    filename = '%sresponse.json' % match.group(1).lower()
    return defer.succeed(loadString(filename))


def add_contained(obj, relname, target):
    '''
    Add and return obj to containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel._setObject(target.id, target)
    return rel._getOb(target.id)


def add_noncontained(obj, relname, target):
    '''
    Add obj to non-containing relname on target.
    '''
    rel = getattr(obj, relname)
    rel.addRelation(target)
