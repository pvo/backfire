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


class FlavorTest(base.BaseIntegrationTest):
    """Test that the flavors portion of the API works as expected."""

    recognized_flavors = {
        'm1.tiny': dict(id=1, name='m1.tiny', ram=512, disk=0),
        'm1.small': dict(id=2, name='m1.small', ram=2048, disk=20),
        'm1.medium': dict(id=3, name='m1.medium', ram=4096, disk=40),
        'm1.large': dict(id=4, name='m1.large', ram=8192, disk=80),
        'm1.xlarge': dict(id=5, name='m1.xlarge', ram=16384, disk=160)}

    def test_list(self):
        """Test that flavors can be listed."""

        # See if we can retrieve the list of flavors
        flavors = self.os.flavors.list()

        # Do we have a list?
        adaptor.assert_not_equal(len(flavors), 0)

        # Let's see if some of our base-line flavors are present
        foundflav = 0
        for flav in flavors:
            if flav.name in self.recognized_flavors:
                exemplar = self.recognized_flavors[flav.name]
                adaptor.assert_equal(flav.id, exemplar['id'])
                adaptor.assert_equal(flav.ram, exemplar['ram'])
                adaptor.assert_equal(flav.disk, exemplar['disk'])
                foundflav += 1

        # Make sure we found our flavors
        adaptor.assert_equal(len(self.recognized_flavors), foundflav)

    def test_get(self):
        """Test that we can get the details of a given flavor."""

        # Check the flavors
        for exemplar in self.recognized_flavors.values():
            flav = self.os.flavors.get(exemplar['id'])

            # Check that all the details match
            adaptor.assert_equal(exemplar['id'], flav.id)
            adaptor.assert_equal(exemplar['name'], flav.name)
            adaptor.assert_equal(exemplar['ram'], flav.ram)
            adaptor.assert_equal(exemplar['disk'], flav.disk)
