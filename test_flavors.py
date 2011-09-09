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
import novaclient

import base

FLAGS = base.FLAGS


class FlavorTest(base.BaseIntegrationTest):
    """Test that the flavors portion of the API works as expected."""

    recognized_flavors = {
        '1': dict(id=1, name='256 slice', ram=256, disk=10),
        '2': dict(id=2, name='512 slice', ram=512, disk=20),
        '3': dict(id=3, name='1GB slice', ram=1024, disk=40),
        '4': dict(id=4, name='2GB slice', ram=2048, disk=80),
        '5': dict(id=5, name='4GB slice', ram=4096, disk=160)}

    def test_list(self):
        """Test that flavors can be listed."""

        # See if we can retrieve the list of flavors
        flavors = self.os.flavors.list()

        # Do we have a list?
        dtutil.assert_not_equal(len(flavors), 0)

        # Let's see if some of our base-line flavors are present
        foundflav = 0
        for flav in flavors:
            if flav.name in self.recognized_flavors:
                exemplar = self.recognized_flavors[flav.name]
                dtutil.assert_equal(flav.id, exemplar['id'])
                dtutil.assert_equal(flav.ram, exemplar['ram'])
                dtutil.assert_equal(flav.disk, exemplar['disk'])
                foundflav += 1

        # Make sure we found our flavors
        dtutil.assert_equal(len(self.recognized_flavors), foundflav)

    def test_get(self):
        """Test that we can get the details of a given flavor."""

        # Check the flavors
        for exemplar in self.recognized_flavors.values():
            flav = self.os.flavors.get(exemplar['id'])

            # Check that all the details match
            dtutil.assert_equal(exemplar['id'], flav.id)
            dtutil.assert_equal(exemplar['name'], flav.name)
            dtutil.assert_equal(exemplar['ram'], flav.ram)
            dtutil.assert_equal(exemplar['disk'], flav.disk)

    def test_get_nonexistent(self):
        """Test that we get an appropriate error for a bad flavor."""

        dtutil.assert_raises(novaclient.exceptions.NotFound,
                             self.os.flavors.get, FLAGS.nonexistent_flavor)
