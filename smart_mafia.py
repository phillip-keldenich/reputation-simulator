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
