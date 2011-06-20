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
import test_servers
import utils


class ServerIpTest(test_servers.BaseServerTest):
    """Test that the server ips API works as expected."""

    def test_get(self):
        """Test that we can get public and private IP addresses."""

        # Grab the server's addresses...
        addrs = self.server.addresses

        # Make sure the public and private lists are present
        adaptor.assert_true('public' in addrs)
        adaptor.assert_true('private' in addrs)

        # Are IP addresses actually returned?

    def test_share(self):
        """Test that we can share an IP address."""

        # In the actual test, we'll want to confirm that an IP address
        # can be shared to a group

        # Try to share with the group--fails for now (operation not
        # implemented in nova); note: change 1 to group, '10.0.0.1' to IP
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.server.share_ip, 1, '10.0.0.1', True)

    def test_unshare(self):
        """Test that we can unshare an IP address."""

        # In the actual test, we'll want to confirm that a shared IP
        # address can be unshared from a group

        # Try to unshare from the group--fails for now (operation not
        # implemented in nova); note: change '10.0.0.1' to IP
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.server.unshare_ip, '10.0.0.1')
