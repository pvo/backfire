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
import sys
import time

import base
import stress

FLAGS = base.FLAGS


class CreateTest(dtest.DTestCase):
    """Test instance create throughput."""

    # Keep track of created instances
    instances = []

    @classmethod
    @dtest.attr(stress=True)
    def tearDownClass(cls):
        """Tear down the create test.

        Deletes all created instances.
        """

        for inst in cls.instances:
            inst.delete()

    def setUp(self):
        """Set up a test run.

        Saves the start time.
        """

        self.start = time.time()

    def tearDown(self):
        """Clean up after a test run.

        Stores the number of creates per minute that were executed in
        the creates_per_min statistics tracker.
        """

        # Get the end time
        end = time.time()

        # We do a number of creates during the time interval, so
        # compute the number of minutes and store the number per
        # minute that were done in our creates_per_min statistics
        # tracker
        ival = (end - self.start) / 60.0

        sample = FLAGS.creates_per_min / ival

        print >>dtest.status, 'Sampled %.2f creates per minute.' % sample

        stress.creates_per_min.append(sample)

    # Now, our tests; we have several identical tests, so start with a
    # helper
    def _do_test(self):
        """Attempt to create an instance."""

        # Append the returned instance to instances so we can clean up
        # later on
        try:
            self.instances.append(stress.mk_instance(None))
        except Exception, e:
            # Print out the exception but otherwise ignore it
            print >>sys.stderr, "Exception %s" % e

    # Now, let's have a few samples
    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample01(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample01)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample02(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample02)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample03(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample03)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample04(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample04)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample05(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample05)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample06(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample06)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample07(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample07)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample08(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample08)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample09(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()

    @dtest.parallel
    @dtest.repeat(FLAGS.creates_per_min)
    @dtest.depends(test_sample09)
    @dtest.timed(FLAGS.timeout * 60)
    @dtest.attr(stress=True)
    def test_sample10(self):
        """Sample the time it takes to perform creates_per_min requests."""

        self._do_test()
