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

import datetime
import time

import dtest


# Resolution is the time between successive status checks; status_ival
# is the (approximate) interval between successive status messages
resolution = 1
status_ival = 10


class StatusTracker(object):
    def __init__(self, *states, **kwargs):
        # Are we case-folding?
        self.foldcase = kwargs.get('foldcase', True)

        # Save the states and fold-case setting
        self.statelist = [s.lower() if self.foldcase else s
                          for s in states[1:]]

        # Initialize the current state and final state
        self.curr_state = states[0].lower() if self.foldcase else states[0]
        self.final_state = states[-1].lower() if self.foldcase else states[-1]

    def checkState(self, newstate):
        # Do a case folding if necessary
        if self.foldcase:
            newstate = newstate.lower()

        # If it's the current state, we're fine...
        if self.curr_state == newstate:
            return None

        # Not current state, let's see if it's one of the next states
        try:
            idx = self.statelist.index(newstate)
        except ValueError:
            # New state is not in the list of valid states!
            return newstate

        # OK, update current state and pare down the list of states
        self.curr_state = self.statelist[idx]
        self.statelist = self.statelist[idx + 1:]

        # We return True only if we hit the end of the states list
        return True if len(self.statelist) == 0 else None

    def waitForState(self, call, attr, *args, **kwargs):
        def getState():
            # Get the object...
            obj = call(*args, **kwargs)

            # Get the current state
            return self.checkState(getattr(obj, attr))

        # Loop until we get to the final state (or hit an invalid
        # state)
        state = getState()
        counter = 0
        start = datetime.datetime.now()
        while state is None:
            # Emit a status message every 5 times (~10 seconds)
            if counter > 0 and counter % (status_ival / resolution) == 0:
                print >>dtest.status, ('Waiting for state "%s"... (%s)' %
                                       (self.final_state,
                                        datetime.datetime.now() - start))
            counter += 1

            time.sleep(resolution)
            state = getState()

        # Return last state; will be True if it's legal or a state
        # string if it's not
        return state
