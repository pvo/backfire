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

"""Package-level global flags are defined here."""


import gflags

# This keeps pylint from barfing on the imports
FLAGS = gflags.FLAGS
DEFINE_string = gflags.DEFINE_string
DEFINE_integer = gflags.DEFINE_integer
DEFINE_bool = gflags.DEFINE_bool

# __GLOBAL FLAGS ONLY__
# Define any app-specific flags in their own files, docs at:
# http://code.google.com/p/python-gflags/source/browse/trunk/gflags.py#39

DEFINE_string('username', 'admin', 'Username to use for authentication')
DEFINE_string('api_key', 'admin', 'API key to use for authentication')
DEFINE_string('auth_url', 'http://localhost:8774/v1.0/',
              'URL to use for authentication')
DEFINE_string('project_id', 'openstack',
              'Project id for the client')
DEFINE_string('second_project', 'openstack',
              'Secondary project id for certain tests')
DEFINE_string('glance_host', 'localhost', 'Host of glance server')
DEFINE_integer('glance_port', 9292, 'Port of glance server')
DEFINE_integer('timeout', 5, 'Timeout, in minutes, for long-running tests')

DEFINE_integer('flavor', 1, 'ID of flavor for built instances')
DEFINE_integer('image', 3, 'ID of image for built instances')

# These flags are necessary to control running the tests
DEFINE_string('directory', None, 'Directory to search for tests to run.')
DEFINE_integer('max_threads', None,
               'The maximum number of tests to run simultaneously.')
DEFINE_string('skip', None,
              'Specifies a rule to control which tests are skipped.')
DEFINE_bool('no_skip', False, 'Specifies that no test should be skipped.')
DEFINE_bool('dry_run', False,
            'Performs a dry run, listing tests without running them.')
DEFINE_bool('debug', False,
            'Enables debugging mode by disabling output capturers.')
DEFINE_string('dot', None, 'Dump a dependency graph to the named file.')
DEFINE_bool('use_dtest', False,
            'Enables using the DTest framework in preference to nose.')
