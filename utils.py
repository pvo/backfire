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

        # Save case-folding
        self.foldcase = kwargs.get('foldcase', True)

        # Save the states 
        self.statelist = states

        # Initialize the current state and final state
        # self.curr_state = states[0]
        self.final_state = states[-1]

        # Initialize the state pointer.
        self.curr_state_idx = 0

    def checkState(self, newstate):
        """Test new state.

        Tests that the given new state is a legal state for the object
        to pass through.  Updates the StatusTracker state to prepare
        for follow-on states.
        """

        for i in range(self.curr_state_idx, len(self.statelist)):
            self.curr_state_idx = i
            if self._statesMatch(self.statelist[i], newstate): 
                if i == len(self.statelist) - 1:
                    return True # matches last state
                else: 
                    return None # matches intermediate state

        return False # does not match any state

    def _statesMatch(self, state1, state2):
        if self.foldcase : return (state1.lower() == state2.lower())
        else : return (state1 == state2)

    def waitForState(self, call, attr, *args, **kwargs):
        """Wait for the final state.

        Waits for the object to enter the final state.  The argument
        'call' is a callable that is passed the extra positional and
        keyword arguments; the attribute 'attr' of the return result
        of the call is expected to be a state.  The callable is called
        in a loop until the state either changes to the final state of
        the tracker (in which case waitForState() returns True) or an
        invalid state is entered (in which case waitForState() returns
        False).  The state of the StatusTracker is modified, so the 
        StatusTracker may not be reused.
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
                print >>dtest.status, ('Waiting for state "%s", currently "%s" (%s)' %
                                       (self.final_state,
                                        getattr(call(*args, **kwargs), attr),
                                        datetime.datetime.now() - start))

            counter += 1

            time.sleep(resolution)
            state = getState()

        # Return last state; will be True if it's legal or False if not
        return state
