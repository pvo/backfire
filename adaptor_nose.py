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

import signal
import sys
import unittest

from nose import core
from nose import case
from nose.plugins import attrib
from nose.plugins import base
from nose.plugins import errorclass
from nose.plugins import skip as nose_skip
from nose import suite
from nose import tools
from nose import util

import flags

FLAGS = flags.FLAGS


# List all the symbols we're interested in
__all__ = [
    'istest', 'nottest', 'skip', 'failing', 'attr', 'depends', 'raises',
    'timed', 'status', 'AdaptedTestCase', 'run_tests',
    ]


# Use unittest.TestCase as our AdaptedTestCase
AdaptedTestCase = unittest.TestCase


# Need a status filehandle
class Status(object):
    def __init__(self):
        self.output = sys.stdout

    def write(self, msg):
        # Write msg out to stdout
        self.output.write(msg)

        # Auto-flush the stream
        self.output.flush()

    def flush(self):
        # Provided for compatibility; this stream auto-flushes
        pass

status = Status()


# Provide some assert functions that are not provided by nose.tools or
# that need to be adapted...
if hasattr(tools, 'assert_not_is_instance'):
    assert_is_not_instance = tools.assert_not_is_instance


# Loop through all remaining assert functions in nose.test and map
# them into the local namespace
for funcname in dir(tools):
    # Skip non-assert functions or ones we have
    if not funcname.startswith('assert_') or funcname in vars():
        continue

    # Copy into our local namespace
    vars()[funcname] = getattr(tools, funcname)


# Now copy over some decorators from nose...
istest = tools.istest
nottest = tools.nottest
attr = attrib.attr
raises = tools.raises


# Need a replacement @timed() decorator which implements dtest's
# semantics, rather than nose's.  This includes an exception to throw
# on timeout, the actual decorator, and a nose plugin to do the right
# thing when the exception is thrown.
class TestTimedOut(Exception):
    """Raise this exception to mark that a test timed out."""

    pass


# The timed decorator
def timed(timeout):
    # Need a signal handler for SIGALRM
    def handler(sig, frame):
        raise TestTimedOut()

    # Actual decorator function
    def decorator(func):
        # Wrap the test function to call, but with a timeout
        def wrapper(*args, **kwargs):
            # First, install the SIGALRM signal handler
            prev_hndlr = signal.signal(signal.SIGALRM, handler)

            try:
                # Set up the alarm
                signal.alarm(timeout)

                # Run the test function
                result = func(*args, **kwargs)
            finally:
                # Stop the alarm
                signal.alarm(0)

                # Restore the signal handler
                signal.signal(signal.SIGALRM, prev_hndlr)

            # Return the result
            return result

        # Replace func with wrapper
        wrapper = tools.make_decorator(func)(wrapper)
        return wrapper

    # Return the actual decorator
    return decorator


# Also need a nose plugin to make timed work properly
class Timed(errorclass.ErrorClassPlugin):
    name = 'timed'
    enabled = True
    timeout = errorclass.ErrorClass(TestTimedOut,
                                    label='TIMEOUT',
                                    isfailure=True)

    def configure(self, options, conf):
        """Configure plugin.  We're always configured."""

        if not self.can_configure:
            return

        self.conf = conf


# Make up a couple other decorators that dtest has which nose doesn't
def skip(func):
    def wrapper(*args, **kwargs):
        # If we're in no-skip mode, make sure to execute the test
        # anyway
        if FLAGS.no_skip:
            return func(*args, **kwargs)

        # Throw a skip exception
        raise nose_skip.SkipTest()

    wrapper = tools.make_decorator(func)(wrapper)
    return wrapper


# failing does nothing at all
def failing(func):
    return func


class DependencyFailed(Exception):
    """Raise this exception to mark that a dependency failed."""

    pass


# depends adds dependencies
def depends(*args):
    def decorator(func):
        # Wrap the test function to check dependencies
        def wrapper(*args, **kwargs):
            for dep in func.dependencies:
                # Check the dependency...
                depresult = DependsPlugin._results.get(dep)
                if not depresult:
                    raise DependencyFailed()

            # OK, run the actual test function
            return func(*args, **kwargs)

        # Set up the _dependencies attribute
        if not hasattr(func, 'dependencies'):
            func.dependencies = set()

        # Attach dependencies to function...
        func.dependencies |= set([getattr(d, 'im_func', d) for d in args])

        # Replace func with wrapper
        wrapper = tools.make_decorator(func)(wrapper)
        return wrapper

    # Return the decorator
    return decorator


# Also need a nose plugin to make DEPFAIL work properly
class DepFail(errorclass.ErrorClassPlugin):
    name = 'depfail'
    enabled = True
    timeout = errorclass.ErrorClass(DependencyFailed,
                                    label='DEPFAIL',
                                    isfailure=True)

    def configure(self, options, conf):
        """Configure plugin.  We're always configured."""

        if not self.can_configure:
            return

        self.conf = conf


# Override the test suite...
class DependsSuite(suite.ContextSuite):
    def _add_func(self, func):
        # Drop function from current dependencies
        self.dependencies.discard(func)

        # Add it to our tests...
        self._ourtests.add(func)

    def _add_deps(self, deps):
        # Add dependencies to our dependencies, excluding our tests
        self.dependencies |= set([d for d in deps
                                  if d not in self._ourtests])

    # Look for fixtures in this context and add their dependencies
    def _explore_fixt(self, names, context):
        for name in names:
            meth = getattr(context, name, None)
            if meth is None:
                continue

            # Need to get the actual function
            func = getattr(meth, '__func__', meth)

            # Add function to our functions
            self._add_func(func)

            # Telescope dependencies up
            if hasattr(func, 'dependencies'):
                self._add_deps(func.dependencies)

            return

    def _find_fixt(self):
        # Determine the context
        context = self.context
        if context is None:
            return

        # Determine which names to look for
        if util.isclass(context):
            setup = self.classSetup
            teardown = self.classTeardown
        else:
            setup = self.moduleSetup
            teardown = self.moduleTeardown
            if hasattr(context, '__path__'):
                setup = self.packageSetup + setup
                teardown = self.packageTeardown + teardown

        # Explore set up and teardown for dependencies
        self._explore_fixt(setup, context)
        self._explore_fixt(teardown, context)

    def _initDeps(self):
        # Make sure dependencies and _ourtests are set up properly;
        # doing this in the constructor fails to work correctly, for
        # some unfathomable reason...
        if not hasattr(self, 'dependencies'):
            self.dependencies = set()
            self._ourtests = set()

            # Deal with fixture dependencies...
            self._find_fixt()

    def addTest(self, test):
        # Make sure dependencies and _ourtests are set up properly
        self._initDeps()

        if isinstance(test, case.Test):
            testmeth = getattr(test.test, test.test._testMethodName)

            # Need to get the actual function
            testfunc = getattr(testmeth, '__func__', testmeth)

            # Add function to our functions
            self._add_func(testfunc)

            # Telescope dependencies up
            if hasattr(testfunc, 'dependencies'):
                self._add_deps(testfunc.dependencies)
        elif isinstance(test, DependsSuite):
            # Make sure dependencies and _ourtests are set up
            # properly
            test._initDeps()

            # Add all the enclosed functions to our own
            for func in test._ourtests:
                self._add_func(func)

            # Telescope dependencies up
            self._add_deps(test.dependencies)

        return super(DependsSuite, self).addTest(test)

    def _get_dependent_tests(self):
        # Determine if a test needs to be skipped due to dependencies
        def skip(test, deps):
            for dep in deps:
                if dep not in DependsPlugin._results:
                    # Push it back onto the end of the todo list
                    return True

            return False

        # Need a space to remember tests we couldn't handle right now
        todo = []

        # Walk through the wrapped tests
        for test in self._get_wrapped_tests():
            deps = None
            if isinstance(test, case.Test):
                testfunc = getattr(test.test, test.test._testMethodName)

                # Grab its dependencies
                deps = getattr(testfunc, 'dependencies', None)
            elif isinstance(test, DependsSuite):
                # Grab its dependencies
                deps = getattr(test, 'dependencies', None)

            # If there are dependencies, evaluate whether they've been
            # tested or not
            if deps and skip(test, deps):
                # We'll wait 'til later...
                todo.append((test, deps))
                continue

            # Yield this test
            yield test

        # Push a sentinel so we can catch looping
        todo.append((None, None))
        looping = True

        # Start walking through the todo list
        while todo:
            # Get a test
            test, deps = todo.pop(0)

            # Are we looping?
            if test is None:
                if looping:
                    # We've tried hard to honor dependencies, but it's
                    # just not possible; go ahead and yield these
                    # tests so they'll DEPFAIL
                    for test, deps in todo:
                        yield test
                    break

                # If we're not at the end, push another sentinel and
                # reset looping
                if todo:
                    todo.append((None, None))
                    looping = True

                continue

            # Evaluate its dependencies again
            if skip(test, deps):
                todo.append((test, deps))
                continue

            # We have a test we can yield!
            looping = False
            yield test

    _tests = property(_get_dependent_tests, suite.LazySuite._set_tests, None,
                      "Access the tests in this suite. Tests are returned "
                      "inside of a context wrapper and ordered based on "
                      "dependencies.")


# Plugin for dependency processing
class DependsPlugin(base.Plugin):
    _results = {}

    name = 'depends'
    enabled = True

    def configure(self, options, conf):
        """Override configure to force ourselves to always be enabled."""

        if not self.can_configure:
            return

        self.conf = conf

        # Force ourself to be enabled
        self.enabled = True

    def addError(self, test, err):
        """Mark that the test failed."""

        if isinstance(test, case.Test):
            testfunc = getattr(test.test, test.test._testMethodName)
            self._results[getattr(testfunc, '__func__', testfunc)] = False
    addFailure = addError

    def addSuccess(self, test):
        """Mark that the test succeeded."""

        if isinstance(test, case.Test):
            testfunc = getattr(test.test, test.test._testMethodName)
            self._results[getattr(testfunc, '__func__', testfunc)] = True

    def prepareTestLoader(self, loader):
        """Change out the suite class to use."""

        loader.suiteClass.suiteClass = DependsSuite


# Finally, one function to run them all...
def run_tests():
    # Consider the directory...
    directory = '.'
    if FLAGS.directory is not None:
        directory = FLAGS.directory

    # Set up the arguments...
    args = [sys.argv[0], '-v', '--exe', directory]

    # Is this a dry run?
    if FLAGS.dry_run:
        args.insert(-2, '--collect-only')
    else:
        # Are we in debug mode?
        if FLAGS.debug:
            args.insert(-2, '--nocapture')

        # Process skip...
        if FLAGS.no_skip:
            args.insert(-2, '--no-skip')
        elif FLAGS.skip:
            args.insert(-2, '--attr=%s' % FLAGS.skip)

    # Run the integration tests
    return core.run(argv=args,
                    addplugins=[Timed(), DepFail(), DependsPlugin()])


# Add the assert functions to __all__
__all__ += [sym for sym in vars().keys() if sym.startswith('assert_')]
