# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import dtest
from dtest import util as dtutil
import novaclient

import base
import utils

FLAGS = base.FLAGS


class BackupScheduleTest(base.BaseIntegrationTest):

    def test_backup_schedules(self):
        """Test the backup schedules.

        This is not yet implemented in Nova.
        """

        server = self.createServer(
            self.randName(prefix="backup_schedule"))

        try:
            # Create a server and a schedule
            server.backup_schedule.create(
                enabled=True,
                weekly=novaclient.BACKUP_WEEKLY_SUNDAY,
                daily=novaclient.BACKUP_DAILY_DISABLED)

            # Get the schedule and verify it is correct
            new_sched = server.backup_schedule.get()
            dtutil.assert_equal(new_sched.enabled, True)
            dtutil.assert_equal(new_sched.weekly,
                                weekly=novaclient.BACKUP_WEEKLY_SUNDAY)
            dtutil.assert_equal(new_sched.daily,
                                novaclient.BACKUP_DAILY_DISABLED)
        except Exception as ex:
            pass
        finally:
            server.delete()
