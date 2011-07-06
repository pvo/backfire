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


class ServerCreationTest(base.BaseIntegrationTest):
    @dtest.attr(longtest=True)
    @dtest.timed(FLAGS.timeout * 60)
    def test_create_delete_server(self):
        """Verify that a server is created and that it is deleted."""

        import pdb; pdb.set_trace()
        # Setup
        server_name = self.randName()
        new_server = self.os.servers.create(name=server_name,
                                            image=FLAGS.image,
                                            flavor=FLAGS.flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        dtutil.assert_true(states.waitForState(self.os.servers.get,
                                               'status', new_server))

        # Verify the server was created correctly
        created_server = self.os.servers.get(new_server.id)
        dtutil.assert_equal(server_name, created_server.name)

        # Delete the server and verify it is removed
        new_server.delete()

        # Legal states...I don't believe it'll ever go to 'deleted',
        # though...
        states = utils.StatusTracker('active', 'build', 'deleted')
        try:
            states.waitForState(self.os.servers.get, 'status', new_server.id)
        except novaclient.NotFound:
            return

    def test_create_bad_flavor(self):
        """Verify that an error is returned if an invalid flavor is requested"""
        dtutil.assert_raises(novaclient.OpenStackException,
                             self.os.servers.create,name='bad_flavor',image=FLAGS.image,flavor=27)

    def test_create_bad_image(self):
        """Verify that an error is returned if an invalid image id is requested"""
        server_name = self.randName()
        dtutil.assert_raises(novaclient.OpenStackException,
                             self.os.servers.create,name='bad_image',image=999999999,flavor=FLAGS.flavor)


class BaseServerTest(base.BaseIntegrationTest):
    """Base class for server-related tests.

    This class contains setUpClass() and tearDownClass()
    implementations that build and delete a server for the tests to
    act upon.  The class attributes manipulated by setUpClass() and
    tearDownClass() are as follows:

    - server
        A handle for the instance created.  This instance is shared
        across all tests inheriting from this class.

    - server_name
        The name of the instance created.

    - flavor
        The integer ID of the flavor the instance was created as.

    - image
        The integer ID of the image the instance was created from.

    - meta_key
        The randomly-generated key of arbitrary metadata associated
        with the instance.

    - meta_val
        The randomly-generated data of the metadata associated with
        the instance.

    Note that setUpClass() is dependent on test_create_delete_server,
    so if that test fails for some reason, all tests in subclasses of
    this class will go to the DEPFAIL state.  This will also happen if
    setUpClass() is unable to create an instance.

    """

    server = None
    server_name = None
    flavor = None
    image = None
    meta_key = None
    meta_val = None

    @classmethod
    @dtest.depends(ServerCreationTest.test_create_delete_server)
    @dtest.timed(FLAGS.timeout * 60)
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
        dtutil.assert_true(states.waitForState(os.servers.get, 'status',
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
        dtutil.assert_equal(int(image.id), int(server.imageId))
        dtutil.assert_equal(int(flavor.id), int(server.flavorId))

    def test_get_nonexistent_server(self):
        """Verify that a request for a nonexistant server fails"""
        dtutil.assert_raises(novaclient.OpenStackException,self.os.servers.get,999999999)

    def test_list_servers(self):
        """Test that the expected servers are returned in a list."""

        # Verify the new server is in the account's list of servers
        server_list = self.os.servers.list()
        found = False
        for s in server_list:
            if s.name == self.server_name:
                found = True
        assert found

    @dtest.timed(FLAGS.timeout * 60)
    @dtest.depends(test_get_server, test_list_servers)
    def test_update_server_name(self):
        """Verify that a server's name can be modified."""

        server = self.server
        self.os.servers.update(server=server.id, name='modifiedName')

        # Verify the server's name has changed
        updated_server = self.os.servers.get(server)
        dtutil.assert_equal('modifiedName', updated_server.name)

