# Copyright 2023 Phillip Keldenich (TU Braunschweig); Sebastian Wild (University of Liverpool)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING 
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import strategies
import morals
import numpy as np
import misc_globals

unsafe = 0.5
semisafe = 0.75
safe = 1.0


# initially, basically the same as mafia
def init_reputation(moral, strats):
    from misc_globals import N

    rep = np.zeros((N,N), float)
    rep[:] = (strats == strategies.smartMafia) * unsafe
    return rep


def get_reputation(r_judging, r_judged):
    # who does not belong to the family must be conquered
    if r_judged == 0.0:
        return 0.0

    if r_judged == safe:
        return 1.0 if r_judging == safe else 0.0
    elif r_judged == semisafe:
        return 1.0 if r_judging >= semisafe else 0.0
    else:
        return 1.0

import misc_globals


def update_reputation(me,moral,my_old_rep,her_old_rep,my_action):
    from implementation import get_neighbors

    if misc_globals.strategies[me] == strategies.smartMafia:
        # a fellow family member!
        neighbors = get_neighbors(me)

        newrep = safe
        for n in neighbors:
            nrep = misc_globals.reputation[moral][n]
            nstrat = misc_globals.strategies[n]

            # if there is an enemy in sight, we are unsafe
            if nstrat != strategies.smartMafia:
                return unsafe
            elif nrep < semisafe:
                newrep = semisafe
        return newrep
    else:
        # an enemy of the family
        return 0.0
