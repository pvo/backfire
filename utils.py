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
    """Track an object through a set of states.

    Helper class designed to assist in testing that an object enters a
    given final state when several intermediate states may also be
    present.  It is instantiated by passing the list of states the
    object is expected to pass through; then the waitForState() method
    is called to wait for the final state.

    Note: Because waitForState() modifies StatusTracker state
    variables, a new StatusTracker object must be initialized each
    time it is used.

    """

    def __init__(self, *states, **kwargs):
        """Initialize a StatusTracker.

        Positional arguments provide an ordered sequence of states
        through which a given object is expected to pass.  If the
        foldcase keyword argument is passed, it is treated as a
        boolean (defaulting to True) which specifies whether to test
        state names case-sensitively (False) or case-insensitively
        (True).
        """

        # Are we case-folding?
        self.foldcase = kwargs.get('foldcase', True)

        # Save the states and fold-case setting
        self.statelist = [s.lower() if self.foldcase else s
                          for s in states[1:]]

        # Initialize the current state and final state
        self.curr_state = states[0].lower() if self.foldcase else states[0]
        self.final_state = states[-1].lower() if self.foldcase else states[-1]

    def checkState(self, newstate):
        """Test new state.

        Tests that the given new state is a legal state for the object
        to pass through.  Updates the StatusTracker state to prepare
        for follow-on states.
        """

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
        """Wait for the final state.

        Waits for the object to enter the final state.  The argument
        'call' is a callable that is passed the extra positional and
        keyword arguments; the attribute 'attr' of the return result
        of the call is expected to be a state.  The callable is called
        in a loop until the state either changes to the final state of
        the tracker (in which case waitForState() returns True) or an
        invalid state is entered (in which case waitForState() returns
        the name of the invalid state).  The state of the
        StatusTracker is modified, so the StatusTracker may not be
        reused.
        """

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
