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

import flags

FLAGS = flags.FLAGS


# List all the symbols we're interested in
__all__ = [
    'istest', 'nottest', 'skip', 'failing', 'attr', 'depends', 'raises',
    'timed', 'status', 'AdaptedTestCase', 'run_tests',
    ]


# Keep our lives simple; do an appropriate conditional import
if FLAGS.use_dtest:
    print "Using DTest"
    from adaptor_dtest import *
else:
    print "Using nose"
    from adaptor_nose import *


# Add the assert functions to __all__
__all__ += [sym for sym in vars().keys() if sym.startswith('assert_')]
