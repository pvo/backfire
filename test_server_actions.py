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

import adaptor
import base
import flags
import test_servers
import utils

FLAGS = flags.FLAGS


class ServerActionTest(base.BaseIntegrationTest):
    """Test that the server actions API works as expected."""

    def setUp(self):
        """Set up an instance for the test."""

        # Call superclass setUp method--sets up self.os
        super(ServerActionTest, self).setUp()

        # Set up the server
        server_name = self.randName()
        server = self.os.servers.create(name=server_name,
                                        image=FLAGS.image,
                                        flavor=FLAGS.flavor)

        # Wait for server to transition to the appropriate state
        states = utils.StatusTracker('active', 'build', 'active')
        states.waitForState(self.os.servers.get, 'status', server)

        # Save the server for later use
        self.server = server

    def tearDown(self):
        """Clean up left-over instances."""

        # Delete the server
        self.server.delete()

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_servers.ServerCreationTest.test_create_delete_server)
    def test_resize_server_confirm(self):
        """Verify that the flavor of a server can be changed."""

        # Resize the server and wait for it to finish
        new_flavor = self.os.flavors.get(2)
        self.server.resize(new_flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'resize-confirm')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

        # Confirm the resize
        self.server.confirm_resize()

        # Check that server's flavor has changed
        self.server = self.os.servers.get(self.server)
        adaptor.assert_equal(new_flavor.id, self.server.flavorId)

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_servers.ServerCreationTest.test_create_delete_server)
    def test_resize_server_revert(self):
        """Verify that a re-sized server can be reverted."""

        # Resize the server and wait for it to finish
        new_flavor = self.os.flavors.get(2)
        self.server.resize(new_flavor)

        # Create list of states
        states = utils.StatusTracker('active', 'resize-confirm')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

        # Revert the resize
        self.server.revert_resize()

        # Check that the was reverted to its original flavor
        self.server = self.os.servers.get(self.server)
        adaptor.assert_equal(new_flavor.id, self.server.flavorId)

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_servers.ServerCreationTest.test_create_delete_server)
    def test_reboot_server(self):
        """Verify that a server can be rebooted."""

        # Verify the server goes through the correct states
        # when rebooting
        states = utils.StatusTracker('active', 'build', 'active')
        self.server.reboot()
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_servers.ServerCreationTest.test_create_delete_server)
    def test_reboot_server_hard(self):
        """Verify that a server can be hard-rebooted."""

        # Verify the server goes through the correct states
        # when rebooting
        states = utils.StatusTracker('active', 'build', 'active')
        self.os.servers.reboot(self.server, type='HARD')
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_servers.ServerCreationTest.test_create_delete_server)
    def test_rebuild_server(self):
        """Verify that a server is created, rebuilt, and then deleted."""

        # Trigger a rebuild
        self.os.servers.rebuild(self.server.id, FLAGS.image)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', self.server))

        # Verify that rebuild acted correctly
        created_server = self.os.servers.get(self.server.id)
        img = self.os.images.get(FLAGS.image)

        adaptor.assert_equal(img.id, created_server.imageId)
