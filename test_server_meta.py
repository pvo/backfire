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

from dtest import util as dtutil

import test_servers
import utils


class ServerMetaTest(test_servers.BaseServerTest):
    """Test that the server metadata API works as expected."""

    def test_list(self):
        """Test that we can retrieve metadata for a server."""

        # Get a pristine server object
        s = self.os.servers.get(self.server)

        # Make sure that we have metadata for this server
        dtutil.assert_not_equal(len(s.metadata), 0)

        # Verify that our metadata key is in there
        dtutil.assert_true(self.meta_key in s.metadata)

        # Verify that it has the value we expect
        dtutil.assert_equal(s.metadata[self.meta_key], self.meta_data)
