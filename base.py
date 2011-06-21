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

import random

import dtest
import novaclient

import flags

FLAGS = flags.FLAGS


class BaseIntegrationTest(dtest.DTestCase):
    """Base integration test.

    This is a base integration test class, which ensures that an
    OpenStack client object is available.

    """

    @staticmethod
    def getOpenStack():
        """Set up and return an OpenStack instance."""

        # Set up the OpenStack instance...
        os = novaclient.OpenStack(FLAGS.username,
                                  FLAGS.api_key,
                                  FLAGS.project_id,
                                  FLAGS.auth_url)

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
