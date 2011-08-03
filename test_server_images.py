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
import test_servers
import utils

FLAGS = base.FLAGS


class ServerImageTest(test_servers.BaseServerTest):
    """Test that the server images API works as expected."""

    @dtest.timed(FLAGS.timeout * 120)
    def test_create_server_image(self):
        """Verify a backup image for a server can be created."""

        # Set legal states
        states = utils.StatusTracker('active', 'queued', 'preparing',
                                     'saving', 'active')

        # Make a backup image for the server
        backup_image = self.os.images.create(server=self.server,
                                             name="backup")
        dtutil.assert_is(True,
                         states.waitForState(self.os.images.get,
                                             'status', backup_image))

        dtutil.assert_equal(backup_image.name, "backup")

        # Cleanup
        self.os.images.delete(backup_image)

    @dtest.attr(longtest=True)
    @dtest.timed(FLAGS.timeout * 120)
    @dtest.depends(test_create_server_image)
    def test_snap_and_restore(self):
        """Verify that a server is snapped and rebuilt from that snap"""

        states = utils.StatusTracker('active', 'queued', 'preparing',
                                     'saving', 'active')

        # Make a backup image for the server
        backup_image = self.os.images.create(server=self.server,
                                             name="backup")
        dtutil.assert_is(True,
                         states.waitForState(self.os.images.get,
                                             'status', backup_image))

        # wrap it in a try so that we can clean up afterwards
        try:
            dtutil.assert_equal(backup_image.name, "backup")

            # Finally, rebuild from the image
            states = utils.StatusTracker('active', 'build', 'active')
            self.os.servers.rebuild(self.server.id, backup_image.id)
            dtutil.assert_is(True,
                             states.waitForState(self.os.servers.get,
                                                 'status', self.server))
            created_server = self.os.servers.get(self.server.id)

            # This has the original image_id out of convention.
            image = self.os.images.get(created_server.imageId)
            dtutil.assert_equal(backup_image.name, image.name)
        finally:
            # delete the image
            self.glance_connection.delete_image(backup_image)
