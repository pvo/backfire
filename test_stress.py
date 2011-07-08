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

import base
import stress

FLAGS = base.FLAGS


class StressTests(dtest.DTestCase):
    """Test Nova under stress."""

    @classmethod
    @dtest.depends(stress.tearDown)
    @dtest.attr(stress=True)
    def setUpClass(cls):
        """Dependency attachment point.

        Simply provides an attachment point for dependencies, to
        ensure the statistics tests contained herein come after the
        tests which generate those statistics.
        """

        pass

    def output_statistics(self, title, stats):
        """Output statistics information."""

        lines = ['%s:' % title]

        # Attach information
        lines.append('        Samples: %d' % len(stats))
        lines.append('        Average: %.2f' % stats.average)
        lines.append('       Std. Dev: %.2f' % stats.stddev)
        lines.append('         Median: %.2f' % stats.median)
        lines.append('90th percentile: %.2f' % stats.percentile90)

        # Now, output it
        print >>dtest.status, '\n    '.join(lines)

    @dtest.attr(stress=True)
    def test_requests(self):
        """Test requests per minute."""

        # First, we'll output the statistics information
        self.output_statistics('Requests per minute', stress.requests_per_min)

        # Now ensure it meets our desired limits
        dtutil.assert_greater_equal(stress.requests_per_min.average,
                                    FLAGS.req_per_min)

    @dtest.attr(stress=True)
    def test_creates(self):
        """Test instance creations per minute."""

        # First, we'll output the statistics information
        self.output_statistics('Instance creates per minute',
                               stress.creates_per_min)

        # Now ensure it meets our desired limits
        dtutil.assert_greater_equal(stress.creates_per_min.average,
                                    FLAGS.creates_per_min)

    @dtest.attr(stress=True)
    def test_request_time(self):
        """Test average request time."""

        # First, we'll output the statistics information
        self.output_statistics('Time per request', stress.request_time)

        # Now ensure it meets our desired limits
        dtutil.assert_less_equal(stress.request_time.average,
                                 FLAGS.request_time)

    @dtest.attr(stress=True)
    def test_create_time(self):
        """Test average instance creation time."""

        # First, we'll output the statistics information
        self.output_statistics('Time per instance creation',
                               stress.create_time)

        # Now ensure it meets our desired limits
        if FLAGS.create_time is not None:
            dtutil.assert_less_equal(stress.create_time.average,
                                     FLAGS.create_time)
