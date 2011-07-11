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
import math
import time

import base
import utils

FLAGS = base.FLAGS


@dtest.skip
@dtest.attr(stress=True)
def setUp():
    """Sets up attribute and skip information for stress tests."""

    pass


@dtest.attr(stress=True)
def tearDown():
    """A convenient hook point for tests on collected statistics."""

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
        self._sorted = None

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
            if len(self._samples) > 0:
                self._avg = sum(self._samples) / len(self._samples)
            else:
                self._avg = 0.0

        return self._avg

    @property
    def stddev(self):
        """Retrieve the standard deviation, with memoization."""

        if self._stddev is None:
            if len(self._samples) > 1:
                tmp = [(p - self.average) ** 2 for p in self._samples]
                self._stddev = math.sqrt(sum(tmp) / (len(tmp) - 1))
            else:
                self._stddev = 0.0

        return self._stddev

    def percentile(self, percent):
        """Retrieve the item representing the percentile.

        The percentile is defined such that the given percentage of
        samples are less than that value.  The percentage should be
        given as a float between 0 and 1.
        """

        if self._sorted is None:
            if len(self._samples) > 0:
                self._sorted = sorted(self._samples)
            else:
                return 0.0

        return self._sorted[int(len(self._sorted) * percent)]

    @property
    def median(self):
        """Retrieve the median item, with memoization.

        The median is defined as the item at index
        round(num_samples * .5).
        """

        return self.percentile(.5)


# Allocate our necessary statistics-tracking items
creates_per_min = Statistics()
create_time = Statistics()
requests_per_min = Statistics()
request_time = Statistics()


# Wrap requests to collect response time information
def wrap_request(call, *args, **kwargs):
    """Wraps call to record start and end times.

    The total time taken to perform the request is stored in the
    request_time statistics tracker.
    """

    # Get the start time of the request
    start = time.time()

    # Make the call
    print "%r(%r, %r)" % (call, args, kwargs)
    response = call(*args, **kwargs)
    print "-> %r" % response

    # Get the end time of the request
    end = time.time()

    # Store this data in our request_time statistics container
    request_time.append((end - start) * 1000.0)

    # Return the response
    return response


class WrapperProxy(object):
    """Class to simplify proxies for wrapping attributes."""

    def __init__(self, wrapped):
        """Initialize WrapperProxy."""

        self._wrapped = wrapped
        self._cache = {}
        self._nocache = set()

    def __getattr__(self, name):
        """Retrieve an attribute.

        If a value for the given name has been cached, returns it;
        otherwise, calls _wrap() with the raw value of the attribute;
        _wrap() must return a tuple consisting of the value to return
        to the caller and True or False depending on whether that
        value should be cached.
        """

        # If name is in the cache, return it
        if name in self._cache:
            return self._cache[name]
        elif name in self._nocache:
            return getattr(self._wrapped, name)

        # OK, call our helper with the real value of the attribute
        value, cache = self._wrap(getattr(self._wrapped, name))

        # Do we cache it?
        if cache is True:
            self._cache[name] = value
        else:
            self._nocache.add(name)

        # Return the value
        return value


class OpenStackProxy(WrapperProxy):
    """Proxy for the internal classes of the OpenStack class."""

    def _wrap(self, value):
        """Wrap callables with wrap_request()."""

        # If value is a callable, use wrap_request
        if callable(value):
            return (lambda *a, **kw: wrap_request(value, *a, **kw)), True

        # Don't cache regular value
        return value, False


class OpenStackWrapped(WrapperProxy):
    """Proxy for the OpenStack class."""

    def _wrap(self, value):
        """Wrap non-callable instances with OpenStackProxy."""

        # Ignore callables...
        if callable(value):
            return value, False

        # Create OpenStackProxy objects for everything else
        return OpenStackProxy(value), True

    @classmethod
    def getOpenStack(cls):
        """Get and return a wrapped OpenStack instance."""

        return cls(base.BaseIntegrationTest.getOpenStack())


# Helper for creating a server--waits for the instance to finish being
# created
def mk_instance(os, *args, **kwargs):
    """Create an instance.

    The os parameter specifies an OpenStack instance to use; may be
    None, in which case one will be set up.  If the provided instance
    is not wrapped by OpenStackWrapped, it will be so wrapped, to
    provide statistics information.  The required creation arguments,
    if not present, will default to appropriate values.  The creation
    time required is tracked in the create_time statistics tracker.

    Returns the created instance, or raises an exception (possibly
    AssertionError) if creation is unsuccessful.
    """

    # Make sure we have an openstack handle
    if not os:
        os = OpenStackWrapped.getOpenStack()

    # Make sure it's wrapped
    if not isinstance(os, OpenStackWrapped):
        os = OpenStackWrapped(os)

    # Also ensure the instance has a name...
    if len(args) < 1 and 'name' not in kwargs:
        kwargs['name'] = base.BaseIntegrationTest.randName()

    # ...an image ID...
    if len(args) < 2 and 'image' not in kwargs:
        kwargs['image'] = FLAGS.image

    # ...and a flavor ID
    if len(args) < 3 and 'flavor' not in kwargs:
        kwargs['flavor'] = FLAGS.flavor

    # We now have the arguments for the create call, but we need to
    # follow it through the required states
    states = utils.StatusTracker('active', 'build', 'active')

    # Now, kick off the create...
    start = time.time()
    new_server = os.servers.create(*args, **kwargs)

    # And wait for it to finish
    dtutil.assert_true(states.waitForState(os.servers.get, 'status',
                                           new_server))
    end = time.time()

    # Store the create time data in our create_time statistics
    # container
    create_time.append((end - start) * 1000.0)

    # Return the new server
    return new_server
