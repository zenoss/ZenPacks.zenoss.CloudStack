##############################################################################
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
##############################################################################

import logging
log = logging.getLogger("zen.migrate")

import Globals
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.MigrateUtils import migratePropertyType


class MigratePassword(ZenPackMigration):
    version = Version(1, 2, 0)

    def migrate(self, dmd):
        log.info("Migrating zCloudStackSecretKey")
        migratePropertyType("zCloudStackSecretKey", dmd, "string")

MigratePassword()
