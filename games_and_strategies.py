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

import numpy as np
from cmdline_args import args
from strategies import *

# Players have 2 actions
cooperate = 0
defect = 1

# The payoff matrix is parametrized by u, the "exploitation payoff"
# (u from Invasion and expansion of cooperators in lattice populations)
# U = 0.6
U = args.U  # use command line argument

# 2x2 Payoff matrix of the game
prisonersDilemma = np.array([[1, 0], [1 + U, U]])
snowdriftGame = np.array([[1, 1 - U], [1 + U, 0]])

payoffs = snowdriftGame if args.game == "SD" else prisonersDilemma
replicatorUpdateMaxScore = 8 * payoffs.max()
pairwiseCooperateScore = 8 * payoffs[cooperate, cooperate]
pairwiseDefectScore = 8 * payoffs[defect, defect]

# all possible combinations of eight payoffs
allPossibleScores = sorted(
    [
        0.0,
        0.125 / (1.0 + U),
        0.25 / (1.0 + U),
        0.375 / (1.0 + U),
        0.5 / (1.0 + U),
        0.625 / (1.0 + U),
        0.75 / (1.0 + U),
        0.875 / (1.0 + U),
        1 / (1.0 + U),
        1.0 / (1.0 + U) - (1.0 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.875 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.875 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.75 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.75 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.75 * U) / (1.0 + U),
        0.625 / (1.0 + U) - (0.625 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.625 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.625 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.625 * U) / (1.0 + U),
        0.5 / (1.0 + U) - (0.5 * U) / (1.0 + U),
        0.625 / (1.0 + U) - (0.5 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.5 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.5 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.5 * U) / (1.0 + U),
        0.375 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        0.5 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        0.625 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.375 * U) / (1.0 + U),
        0.25 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.375 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.5 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.625 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.25 * U) / (1.0 + U),
        0.125 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.25 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.375 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.5 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.625 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.75 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.875 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        1.0 / (1.0 + U) - (0.125 * U) / (1.0 + U),
        0.125,
        0.25 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.375 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.5 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.625 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.125 * U) / (1.0 + U),
        0.25 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.375 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.5 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.625 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.25 * U) / (1.0 + U),
        0.375 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        0.5 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        0.625 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.375 * U) / (1.0 + U),
        0.5 / (1.0 + U) + (0.5 * U) / (1.0 + U),
        0.625 / (1.0 + U) + (0.5 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.5 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.5 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.5 * U) / (1.0 + U),
        0.625 / (1.0 + U) + (0.625 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.625 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.625 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.625 * U) / (1.0 + U),
        0.75 / (1.0 + U) + (0.75 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.75 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.75 * U) / (1.0 + U),
        0.875 / (1.0 + U) + (0.875 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (0.875 * U) / (1.0 + U),
        1.0 / (1.0 + U) + (1.0 * U) / (1.0 + U),
    ]
)


def rank_reduce_score(score):
    rr = score - score
    for s in allPossibleScores:
        rr += score >= s
    return (rr - 1.0) / 80.0


import morals

strategyMoral = {
    allDefect: morals.dontCare,
    allCooperate: morals.dontCare,
    saferep: morals.saferep,
    mafia: morals.laFamilia,
    democrats: morals.liberal,
    democrats2: morals.liberal2,
    republicans2: morals.saferep2,
    kandori1: morals.kandori1,
    kandori2: morals.kandori2,
    kandori3: morals.kandori3,
    kandori8: morals.kandori8,
    kandori9: morals.kandori9,
    kandoriInitiallyGood: morals.kandoriInitiallyGood,
    safedirep: morals.safedirep,
    safedirep2: morals.safedirep2,
    smartMafia: morals.smartMafia,
    mafia2: morals.laFamilia2,
}

import smart_mafia


# The 'implementation' of all strategies, given as a function returning
# the probability that the player will play "cooperate"
def action(strategy, R_you):
    if strategy == allDefect:
        return defect
    elif strategy == allCooperate:
        return cooperate
    elif strategy in discriminatorStrategies:
        return cooperate if R_you >= 0.5 else defect
