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

import novaclient

import adaptor
import flags
import test_servers
import utils

FLAGS = flags.FLAGS


class ServerImageTest(test_servers.BaseServerTest):
    """Test that the server images API works as expected."""

    @adaptor.timed(FLAGS.timeout * 120)
    def test_create_server_image(self):
        """Verify a backup image for a server can be created."""

        # Set legal states
        states = utils.StatusTracker('active', 'queued', 'preparing',
                                     'saving', 'active')

        # Make a backup image for the server
        backup_image = self.os.images.create("backup", self.server)
        adaptor.assert_true(states.waitForState(self.os.images.get,
                                                'status', backup_image))

        adaptor.assert_equal(backup_image.name, "backup")

    @adaptor.attr(longtest=True)
    @adaptor.timed(FLAGS.timeout * 120)
    def test_snap_and_restore(self):
        """Verify that a server is snapped and rebuilt from that snap"""

        states = utils.StatusTracker('active', 'queued', 'preparing',
                                     'saving', 'active')

        # Make a backup image for the server

        backup_image = self.os.images.create("backup", self.server)
        adaptor.assert_true(states.waitForState(self.os.images.get,
                                                'status', backup_image))

        adaptor.assert_equal(backup_image.name, "backup")
         

        # Finally, rebuild from the image
        states = utils.StatusTracker('active', 'build', 'active')
        self.os.servers.rebuild(self.server.id, backup_image.id)
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

        created_server = self.os.servers.get(self.server.id)

        adaptor.assert_equal(backup_image.id, created_server.imageId)
