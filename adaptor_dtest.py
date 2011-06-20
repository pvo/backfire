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
from dtest import util

from integration import flags

FLAGS = flags.FLAGS


# List all the symbols we're interested in
__all__ = [
    'istest', 'nottest', 'skip', 'failing', 'attr', 'depends', 'raises',
    'timed', 'status', 'AdaptedTestCase', 'run_tests',
    ]


# Use DTestCase as our AdaptedTestCase
AdaptedTestCase = dtest.DTestCase


# Need a status filehandle
status = dtest.status


# Provide some assert functions that are not provided by dtest.util or
# that need to be adapted...
def assert_raises_regexp(expected_exception, expected_regexp,
                         callable_obj=None, *args, **kwargs):
    return util.assert_raises(expected_exception, callableObj=callable_obj,
                              matchRegExp=expected_regexp, *args, **kwargs)


assert_not_is_instance = util.assert_is_not_instance


def assert_dict_contains_subset(expected, actual, msg=None):
    return util.assert_dict_contains(actual, expected, msg=msg)


# Loop through all remaining assert functions in dtest.util and map
# them into the local namespace
for funcname in dir(util):
    # Skip non-assert functions or ones we have
    if not funcname.startswith('assert_') or funcname in vars():
        continue

    # Copy into our local namespace
    vars()[funcname] = getattr(util, funcname)


# Now copy over some decorators from dtest...
istest = dtest.istest
nottest = dtest.nottest
skip = dtest.skip
failing = dtest.failing
attr = dtest.attr
depends = dtest.depends
raises = dtest.raises
timed = dtest.timed


# Finally, one function to run them all...
def run_tests():
    # Build the arguments for running main()
    args = {}
    if FLAGS.no_skip:
        args['skip'] = lambda dt: False
    elif FLAGS.skip is not None:
        if '=' in FLAGS.skip:
            k, v = FLAGS.skip.split('=', 1)
            args['skip'] = lambda dt: getattr(dt, k, None) == v
        else:
            args['skip'] = lambda dt: hasattr(dt, FLAGS.skip)

    # Set up maximum number of threads
    if FLAGS.max_threads is not None:
        args['maxth'] = FLAGS.max_threads

    # Are we doing a dry run?
    if FLAGS.dry_run:
        args['dryrun'] = True

    # Are we in debug mode?
    if FLAGS.debug:
        args['debug'] = True

    # Dumping the dependency graph?
    if FLAGS.dot is not None:
        args['dotpath'] = FLAGS.dot

    # Finally, consider the directory
    if FLAGS.directory is not None:
        args['directory'] = FLAGS.directory

    # Run the integration tests
    return dtest.main(**args)


# Add the assert functions to __all__
__all__ += [sym for sym in vars().keys() if sym.startswith('assert_')]
