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
import math
import time

import test_servers

@dtest.attr(stress=True)
@dtest.skip
def setUp():
    """Sets up attribute and skip information for stress tests."""

    pass


class Statistics(object):
    """Class to simplify collection of statistics."""

    def __init__(self):
        """Initialize statistics."""

        self._samples = []
        self._reset()

    def append(self, sample):
        """Add a sample to the statistics object."""

        self._samples.append(sample)
        self._reset()

    def _reset(self):
        """Reset internal memoization fields."""

        self._avg = None
        self._stddev = None
        self._sorted = []

    def __len__(self):
        """Return the number of samples."""

        return len(self._samples)

    def __getitem__(self, key):
        """Retrieve a given sample."""

        return self._samples[key]

    @property
    def average(self):
        """Retrieve the average of the samples, with memoization."""

        if self._avg is None:
            self._avg = sum(self._samples) / len(self._samples)

        return self._avg

    @property
    def stddev(self):
        """Retrieve the standard deviation, with memoization."""

        if self._stddev is None:
            tmp = [(p - self.average) ** 2 for p in self._samples]
            self._stddev = math.sqrt(sum(tmp) / (len(tmp) - 1))

        return self._stddev

    @property
    def median(self):
        """Retrieve the median item, with memoization.

        The median is defined as the item at index
        ceil(num_samples * .5).
        """

        if self._sorted is None:
            self._sorted = sorted(self._samples)

        return self._sorted[int(math.ceil(len(self._sorted) * .5))]

    @property
    def percentile90(self):
        """Retrieve the 90th percentile item, with memoization.

        The 90th percentile item is defined as the item at index
        ceil(num_samples * .9).
        """

        if self._sorted is None:
            self._sorted = sorted(self._samples)

        return self._sorted[int(math.ceil(len(self._sorted) * .9))]


# Allocate our necessary statistics-tracking items
creates_per_min = Statistics()
requests_per_min = Statistics()
response_time = Statistics()


# Wrap requests to collect response time information
def wrap_request(call, *args, **kwargs):
    # Get the start time of the request
    start = time.time()

    # Make the call
    response = call(*args, **kwargs)

    # Get the end time of the request
    end = time.time()

    # Store this data in our response_time statistics container
    response_time.append(end - start)

    # Return the response
    return response
