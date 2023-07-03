from misc_globals import N

# Define different morals
saferep = 1
dontCare = 2
laFamilia = 3
kandori1 = 4
kandori2 = 5
kandori3 = 6
kandori8 = 7
kandori9 = 8
liberal = 9
liberal2 = 10
saferep2 = 11
kandoriInitiallyGood = 12
safedirep = 13
safedirep2 = 14
smartMafia = 15
laFamilia2 = 16

# polarization seed = 0 if moral in polarizationSeedScepticMorals else 1
polarizationSeedScepticMorals = [saferep, liberal2, safedirep2]

saferepAgainstGoodBits = {}
saferepAgainstBadBits = {}

# in kandoryHistory, we store for each general kandori1 moral a NxN array of kandori1 states
# the states are in {-T,...,-1,0}, where T is given by kandoriPenaltyLoop[moral]
# Semantics of the values:
#    = 0  means good,
#    < 0  means bad
kandoriHistory = {}

moralNames = {
    saferep: "saferep",
    dontCare: "dontCare",
    laFamilia: "laFamilia",
    laFamilia2: "laFamilia2",
    kandori1: "Kandori(T=1)",
    kandori2: "Kandori(T=2)",
    kandori3: "Kandori(T=3)",
    kandori8: "Kandori(T=8)",
    kandori9: "Kandori(T=9)",
    liberal: "liberal",
    liberal2: "liberal2",
    saferep2: "saferep2",
    kandoriInitiallyGood: "kandoriInitiallyGood",
    safedirep: "safedirep",
    safedirep2: "safedirep2",
    smartMafia: "smartMafia",
}
# The reputation functions have to be configured at the end of this file

# morals that are not interesting are not shown in GUI and are not used for stats
uninterestingMorals = [dontCare, laFamilia]

import games_and_strategies
import numpy as np

initialAgainstGoodAction = {
    saferep: games_and_strategies.cooperate,
    liberal: games_and_strategies.cooperate,
    saferep2: games_and_strategies.cooperate,
    liberal2: games_and_strategies.cooperate,
    safedirep: games_and_strategies.cooperate,
    safedirep2: games_and_strategies.cooperate,
}

initialAgainstBadAction = {
    saferep: games_and_strategies.cooperate,
    liberal: games_and_strategies.defect,
    liberal2: games_and_strategies.defect,
    saferep2: games_and_strategies.cooperate,
    safedirep: games_and_strategies.defect,
    safedirep2: games_and_strategies.cooperate,
}

# config for general Kandori reputation, see
# https://www.ibr.cs.tu-bs.de/trac/algogame/wiki/RepEvolST%20-%20Literatur?version=14#Relevantf%C3%BCruns

# T values
kandoriPenaltyLoop = {
    kandori1: 1,
    kandori2: 2,
    kandori3: 3,
    kandori8: 8,
    kandori9: 9,
    kandoriInitiallyGood: 8,
}


def initSaferep(moral, strategies):
    saferepAgainstGoodBits[moral] = (
        np.ones((N, N), int) * initialAgainstGoodAction[moral]
    )
    saferepAgainstBadBits[moral] = np.ones((N, N), int) * initialAgainstBadAction[moral]
    initialRep = (
        1
        if initialAgainstGoodAction[moral] == games_and_strategies.cooperate
        and initialAgainstBadAction[moral] == games_and_strategies.defect
        else 0
    )
    return np.zeros((N, N), int) + initialRep


def initKandori(moral, strategies):
    kandoriHistory[moral] = np.zeros((N, N), int) - kandoriPenaltyLoop[moral]
    if moral == kandoriInitiallyGood:
        kandoriHistory[moral][:] = 0  # hack all to start as good
        return np.ones((N, N), int)
    return np.zeros((N, N), int)


def initLaFamilia(moral, strategies):
    rep = np.zeros((N, N), int)
    rep[:] = strategies == games_and_strategies.mafia
    return rep


def initLaFamilia2(moral, strategies):
    rep = np.zeros((N, N), int)
    rep[:] = strategies == games_and_strategies.mafia2
    return rep


def moralByName(moralName):
    for moral in moralNames.keys():
        if moralName == moralNames[moral]:
            return moral
    return -1  # none found


import reputation_updates
from safedirep import initSafedirep
import smart_mafia

initMoral = {
    saferep: initSaferep,
    liberal: initSaferep,
    liberal2: initSaferep,
    saferep2: initSaferep,
    kandori1: initKandori,
    kandori2: initKandori,
    kandori3: initKandori,
    kandori8: initKandori,
    kandori9: initKandori,
    kandoriInitiallyGood: initKandori,
    laFamilia: initLaFamilia,
    laFamilia2: initLaFamilia2,
    dontCare: lambda moral, strategies: np.zeros((N, N), int),
    safedirep: initSafedirep,
    safedirep2: initSafedirep,
    smartMafia: smart_mafia.init_reputation,
}


# The reputation update functions for the morals;
# The signature is as follows, where "me" refers to the player getting his reputation updated
# and "her" refers to the other player:
# repUpdate(me, myMoral, my_old_rep, her_old_rep, my_action) returning the new reputation
newReputation = {
    saferep: reputation_updates.saferep,
    liberal: reputation_updates.saferep,
    liberal2: reputation_updates.saferep,
    saferep2: reputation_updates.saferep,
    dontCare: reputation_updates.amoral,
    kandori1: reputation_updates.genericKandori,
    laFamilia: reputation_updates.neverBetrayTheFamily,
    laFamilia2: reputation_updates.neverBetrayTheOtherFamily,
    kandori2: reputation_updates.genericKandori,
    kandori3: reputation_updates.genericKandori,
    kandori8: reputation_updates.genericKandori,
    kandori9: reputation_updates.genericKandori,
    kandoriInitiallyGood: reputation_updates.genericKandori,
    safedirep: reputation_updates.saferep,
    safedirep2: reputation_updates.saferep,
    smartMafia: smart_mafia.update_reputation,
}
