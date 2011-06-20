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
import base
import flags
import utils

FLAGS = flags.FLAGS


class ServerCreationTest(base.BaseIntegrationTest):
    @adaptor.attr(longtest=True)
    @adaptor.timed(FLAGS.timeout * 60)
    def test_create_delete_server(self):
        """Verify that a server is created and that it is deleted."""

        # Setup
        server_name = self.randName()
        new_server = self.os.servers.create(name=server_name,
                                            image=FLAGS.image,
                                            flavor=FLAGS.flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', new_server))

        # Verify the server was created correctly
        created_server = self.os.servers.get(new_server.id)
        adaptor.assert_equal(server_name, created_server.name)

        # Delete the server and verify it is removed
        new_server.delete()

        # Legal states...I don't believe it'll ever go to 'deleted',
        # though...
        states = utils.StatusTracker('active', 'build', 'deleted')
        try:
            states.waitForState(self.os.servers.get, 'status', new_server.id)
        except novaclient.NotFound:
            return
    
    @adaptor.attr(longtest=True)
    @adaptor.timed(FLAGS.timeout * 60)
    def test_rebuild_server(self):
        """Verify that a server is created, rebuilt, and then deleted."""

        # Setup
        server_name = self.randName()
        new_server = self.os.servers.create(name=server_name,
                                            image=FLAGS.image,
                                            flavor=FLAGS.flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', new_server))

        # Verify the server was created correctly
        created_server = self.os.servers.get(new_server.id)
        adaptor.assert_equal(server_name, created_server.name)
        self.os.servers.rebuild(new_server.id, FLAGS.image)

        adaptor.assert_true(states.waitForState(self.os.servers.get,
                                                'status', new_server))

        created_server = self.os.servers.get(new_server.id)
        adaptor.assert_equal(server_name, created_server.name)
        img = self.os.images.get(FLAGS.image)

        adaptor.assert_equal(img.id, created_server.imageId)


        # Delete the server and verify it is removed
        new_server.delete()

        # Legal states...I don't believe it'll ever go to 'deleted',
        # though...
        states = utils.StatusTracker('active', 'build', 'deleted')
        adaptor.assert_raises(novaclient.NotFound, states.waitForState,
                              self.os.servers.get, 'status', new_server.id)

class BaseServerTest(base.BaseIntegrationTest):
    """Base class for server-related tests.

    This class contains setUpClass() and tearDownClass()
    implementations that build and delete a server for the tests to
    act upon.

    """

    server = None
    server_name = None
    flavor = None
    image = None
    meta_key = None
    meta_val = None

    @classmethod
    @adaptor.depends(ServerCreationTest.test_create_delete_server)
    @adaptor.timed(FLAGS.timeout * 60)
    def setUpClass(cls):
        """Set up an instance for use by the enclosed tests."""

        # Need an OpenStack instance so we can create the server
        os = cls.getOpenStack()

        # Select a random key and value for metadata; used by the
        # metadata tests
        cls.meta_key = cls.randName(length=10)
        cls.meta_data = cls.randName(length=50)

        # Set up the server
        cls.flavor = FLAGS.flavor
        cls.image = FLAGS.image
        cls.server_name = cls.randName()
        cls.server = os.servers.create(name=cls.server_name,
                                       image=cls.image, flavor=cls.flavor,
                                       meta={cls.meta_key: cls.meta_data})

        # Wait for the server to transition to the appropriate state
        states = utils.StatusTracker('active', 'build', 'active')
        adaptor.assert_true(states.waitForState(os.servers.get, 'status',
                                                cls.server))

    @classmethod
    def tearDownClass(cls):
        """Clean up the instance created by setUpClass()."""

        # Delete the server
        cls.server.delete()


class ServerTest(BaseServerTest):
    """Test that the servers API works as expected."""

    def test_get_server(self):
        """Test that the expected server details are returned."""

        # Verify the server fields are correct
        flavor = self.os.flavors.get(self.flavor)
        image = self.os.images.get(self.image)
        server = self.os.servers.get(self.server)
        adaptor.assert_equal(int(image.id), int(server.imageId))
        adaptor.assert_equal(int(flavor.id), int(server.flavorId))

    def test_list_servers(self):
        """Test that the expected servers are returned in a list."""

        # Verify the new server is in the account's list of servers
        server_list = self.os.servers.list()
        found = False
        for s in server_list:
            if s.name == self.server_name:
                found = True
        assert found

    @adaptor.timed(FLAGS.timeout * 60)
    @adaptor.depends(test_get_server, test_list_servers)
    def test_update_server_name(self):
        """Verify that a server's name can be modified."""

        server = self.server
        self.os.servers.update(server=server.id, name='modifiedName')

        # Verify the server's name has changed
        updated_server = self.os.servers.get(server)
        adaptor.assert_equal('modifiedName', updated_server.name)
