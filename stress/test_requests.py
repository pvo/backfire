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
import time

import base
import stress
from stress import test_creates

FLAGS = base.FLAGS


class RequestTest(dtest.DTestCase):
    """Test request throughput."""

    @classmethod
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.depends(test_creates.CreateTest.tearDownClass)
    def setUpClass(cls):
        """Set up the request test.

        Allocates an OpenStack connection and creates an instance for
        the tests.
        """

        # First, allocate an OpenStack connection
        cls.os = stress.OpenStackWrapped.getOpenStack()

        # Now, we need to make an instance
        cls.server = stress.mk_instance(cls.os)

    @classmethod
    def tearDownClass(cls):
        """Tear down the request test.

        Cleans up the instance we allocated in setUpClass().
        """

        cls.server.delete()

    def setUp(self):
        """Set up a test run.

        Saves the start time.
        """

        self.start = time.time()

    def tearDown(self):
        """Clean up after a test run.

        Stores the number of requests per minute that were executed in
        the requests_per_min statistics tracker.
        """

        # Get the end time
        end = time.time()

        # We do a number of requests during the time interval, so
        # compute the number of minutes and store the number per
        # minute that were done in our requests_per_min statistics
        # tracker
        ival = (end - self.start) / 60.0

        sample = FLAGS.req_per_min / ival

        print >>dtest.status, 'Sampled %.2f requests per minute.' % sample

        stress.requests_per_min.append(sample)

    # Now, our tests; we have several identical tests, so start with a
    # helper
    def _do_test(self):
        """Attempt to retrieve the status of the instance."""

        # Simply retrieve the status from the server
        dtutil.assert_equal(self.os.servers.get(self.server).status.lower(),
                            'active')

    # Now, let's have a few samples
    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.attr(stress=True)
    def test_sample01(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample01)
    @dtest.attr(stress=True)
    def test_sample02(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample02)
    @dtest.attr(stress=True)
    def test_sample03(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample03)
    @dtest.attr(stress=True)
    def test_sample04(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample04)
    @dtest.attr(stress=True)
    def test_sample05(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample05)
    @dtest.attr(stress=True)
    def test_sample06(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample06)
    @dtest.attr(stress=True)
    def test_sample07(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample07)
    @dtest.attr(stress=True)
    def test_sample08(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample08)
    @dtest.attr(stress=True)
    def test_sample09(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.req_per_min)
    @dtest.depends(test_sample09)
    @dtest.attr(stress=True)
    def test_sample10(self):
        """Sample the time it takes to perform req_per_min requests."""

        self._do_test()
