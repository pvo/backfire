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

import dtest

import base


if __name__ == '__main__':
    # First, pull in the DTest options
    opts = dtest.optparser(usage="%prog [options]")

    # Add on backfire-specific options
    base.add_opts(opts)

    # Process command-line arguments
    (options, args) = opts.parse_args()

    # Extract the backfire-specific options into storage everything
    # can get to; also handles some defaults
    base.extract_opts(options)

    # Run the tests
    sys.exit(not dtest.main(**opts_to_args(options)))
