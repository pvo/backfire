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

import os
import random
import urlparse

import dtest
import novaclient


FLAGS = None


def add_opts(opts):
    """Add options.

    Used to extend the list of available options that DTest provides
    with options specific to the test suite.  You should set up
    reasonable defaults for any options added here.
    """

    # Get the default nova URL and glance host
    def_nova_url = os.environ.get('NOVA_URL', 'http://localhost:8774/v1.0/')
    def_glance_host = urlparse.urlparse(def_nova_url).hostname or 'localhost'

    opts.add_option("--username",
                    action="store", type="string", dest="username",
                    default=os.environ.get('NOVA_USERNAME', 'admin'),
                    help="The username to use for authentication "
                    "[default %default].")
    opts.add_option("--api-key",
                    action="store", type="string", dest="api_key",
                    default=os.environ.get('NOVA_API_KEY'),
                    help="The API key to use for authentication.")
    opts.add_option("--nova-url",
                    action="store", type="string", dest="nova_url",
                    default=def_nova_url,
                    help="The URL to use for authentication "
                    "[default %default].")
    opts.add_option("--project-id",
                    action="store", type="string", dest="project_id",
                    default=os.environ.get('NOVA_PROJECT_ID', 'openstack'),
                    help="The project ID for the client [default %default].")
    opts.add_option("--second-project",
                    action="store", type="string", dest="second_project",
                    help="Secondary project ID for certain tests.  If not "
                    "specified, defaults to the value of --project-id.")
    opts.add_option("--glance-host",
                    action="store", type="string", dest="glance_host",
                    default=def_glance_host,
                    help="Host of glance server [default %default].")
    opts.add_option("--glance-port",
                    action="store", type="int", dest="glance_port",
                    default=9292,
                    help="Port of glance server [default %default].")
    opts.add_option("--timeout",
                    action="store", type="int", dest="timeout",
                    default=5,
                    help="Timeout, in minutes, for long-running tests "
                    "[default %default].")
    opts.add_option("--flavor",
                    action="store", type="int", dest="flavor",
                    default=1,
                    help="ID of flavor for built instances "
                    "[default %default].")
    opts.add_option("--image",
                    action="store", type="int", dest="image",
                    default=3,
                    help="ID of image for built instances [default %default].")
    opts.add_option("--test-image",
                    action="store", type="string", dest="test_image",
                    default="test_image.img",
                    help="Image to use for basic image tests "
                    "[default %default].")


def extract_opts(options):
    """Extract test suite-specific options.

    Saves the options and performs final handling of defaults that
    cannot be expressed easily (such as --second-project defaulting to
    --project-id).
    """

    global FLAGS

    # Save the options
    FLAGS = options

    # Set up the default of second_project
    if FLAGS.second_project is None:
        FLAGS.second_project = FLAGS.project_id


class BaseIntegrationTest(dtest.DTestCase):
    """Base integration test.

    This is a base integration test class, which ensures that an
    OpenStack client object is available.  A setUp() method is
    included which sets self.os to be an instance of
    novaclient.OpenStack().

    """

    @staticmethod
    def getOpenStack():
        """Set up and return an OpenStack instance."""

        # Set up the OpenStack instance...
        os = novaclient.OpenStack(FLAGS.username,
                                  FLAGS.api_key,
                                  FLAGS.project_id,
                                  FLAGS.nova_url)

        # Do the authenticate now, so we fail early
        os.authenticate()

        return os

    def setUp(self):
        """For each test, set up an OpenStack instance."""

        # Get an OpenStack instance
        self.os = self.getOpenStack()

    @staticmethod
    def randName(length=20, charset="abcdefghijklmnopqrstuvwxyz"):
        """Generate a random name of the given length."""

        return ''.join([charset[random.randrange(len(charset))]
                        for i in xrange(length)])
