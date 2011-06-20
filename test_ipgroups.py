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

from integration import adaptor
from integration import base


class IpGroupTest(base.BaseIntegrationTest):
    """Test that the IP groups API works as expected."""

    def test_create(self):
        """Test that we can create an IP group."""

        # Start by creating a random IP group name
        name = self.randName()

        # Try to create the group--fails for now (operation not
        # implemented in nova)
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.os.ipgroups.create, name)

    def test_delete(self):
        """Test that we can delete an IP group."""

        # In the actual test, we'll want to create a group for
        # delete() to act on here

        # Try to delete the group--fails for now (operation not
        # implemented in nova)
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.os.ipgroups.delete, 1)  # change 1 to group

    def test_get(self):
        """Test that we can get the details of an IP group."""

        # In the actual test, we'll want to create a group for get()
        # to act on here

        # Try to get the group--fails for now (operation not
        # implemented in nova)
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.os.ipgroups.get, 1)  # change 1 to group

    def test_list(self):
        """Test that we can list the details of an IP group."""

        # In the actual test, we'll want to create a group or two for
        # list() to act on here

        # Try to list the groups--fails for now (operation not
        # implemented in nova)
        adaptor.assert_raises(novaclient.OpenStackException,
                              self.os.ipgroups.list)
