#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import gettext
import os
import sys

import flags

FLAGS = flags.FLAGS


if __name__ == '__main__':
    # Process command-line flags
    argv = FLAGS(sys.argv)

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
    sys.exit(dtest.main(**args))
