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
from glance import client as glanceclient
import novaclient

import base
import utils

FLAGS = base.FLAGS


class ServerCreationTest(base.BaseIntegrationTest):
    @dtest.attr(longtest=True)
    @dtest.timed(FLAGS.timeout * 60)
    def test_create_delete_server(self):
        """Verify that a server is created and that it is deleted."""

        # Setup
        server_name = self.randName()
        new_server = self.create_server(server_name,
                                       FLAGS.image,
                                       FLAGS.flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        dtutil.assert_is(True,
                         states.waitForState(self.os.servers.get,
                                             'status', new_server))

        # Verify the server was created correctly
        created_server = self.os.servers.get(new_server.id)
        dtutil.assert_equal(server_name, created_server.name)

        # Delete the server.  The delete testing is moved to
        # test_delete
        new_server.delete()

    @dtest.attr(longtest=True)
    @dtest.timed(FLAGS.timeout * 60)
    def test_create_from_bad_image(self):
        """Verify a bad image will not boot"""

        # Create a bad image
        new_meta = self.create_glance_image(file_name=FLAGS.bad_test_image,
                                          image_name=self.randName(
                                              prefix='bad_image'))

        try:
            # Boot the bad image
            server_name = self.randName(prefix='bad_image')
            new_server = self.create_server(server_name,
                                           new_meta['id'],
                                           FLAGS.flavor)

            # Specify expeted states
            states = utils.StatusTracker('build', 'error')

            # Verify state transition
            dtutil.assert_is(True,
                             states.waitForState(self.os.servers.get,
                                                 'status',
                                                 new_server))
        finally:
            # Cleanup
            self.glance_connection.delete_image(new_meta['id'])
            self.os.servers.delete(new_server)

    @dtest.attr(longtest=True)
    @dtest.timed(FLAGS.timeout * 60)
    def test_delete(self):
        """Verify servers can be deleted.

        This logically belongs in test_create_delete_server,
        which is a dependency for all the other tests. However,
        this test fails due to Nova bug #793785
        """

        server_name = self.randName()
        new_server = self.create_server(server_name, FLAGS.image, FLAGS.flavor)

        # Legal states...
        states = utils.StatusTracker('active', 'build', 'active')

        # Wait for server to transition to next state and make sure it
        # went to the correct one
        states.waitForState(self.os.servers.get, 'status', new_server)

        # Delete the server and verify it is removed
        new_server.delete()

        # Legal states. Nova bug #793785
        # Status goes through 'build' when deleting, but should not.
        states = utils.StatusTracker('active', 'deleted')

        # Verify that state goes to "deleted", or raises NotFound exception.
        try:
            dtutil.assert_is(True,
                             states.waitForState(self.os.servers.get,
                                                 'status', new_server))
        except novaclient.exceptions.NotFound:
            pass

    def test_create_from_nonexistent_flavor(self):
        """Verify an error is returned if an invalid flavor is requested"""
        dtutil.assert_raises(novaclient.OpenStackException,
                             self.os.servers.create,
                             name='nonexistent_flavor',
                             image=FLAGS.image,
                             flavor=FLAGS.nonexistent_flavor)

    def test_create_from_nonexistent_image(self):
        """Verify an error is returned if an invalid image id is requested"""
        server_name = self.randName()
        dtutil.assert_raises(novaclient.OpenStackException,
                             self.os.servers.create,
                             name='nonexistent_image',
                             image=FLAGS.nonexistent_image,
                             flavor=FLAGS.flavor)


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
        dtutil.assert_is(True,
                         states.waitForState(os.servers.get, 'status',
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
        dtutil.assert_raises(novaclient.OpenStackException,
                self.os.servers.get,
                FLAGS.nonexistent_image)

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
