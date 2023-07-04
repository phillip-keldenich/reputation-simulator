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
import time, sys
from cmdline_args import args

from games_and_strategies import payoffs, strategyMoral, replicatorUpdateMaxScore

from misc_globals import (
    strategies,
    reputation,
    N,
    M,
    bernoulli,
    occurringStrategiesNames,
    neighbor_offsets,
    neighbor_offsets_index,
    occurringMorals,
    duelSelectionRandom,
    HEAVEN,
    HELL,
)

import config
import morals
import display_config

import games_and_strategies
import stats as statistics
import safedirep
import smart_mafia

# python3 support - this works regardless of python version.
try:
    xrange
except NameError:
    xrange = range

# The polarizing player
polarizingPlayer = config.polarizingPlayer

# Seed for polarization
repInitPolarizationSeed = args.polarization_seed

# The current iteration
iteration = 0

# The number of strategies occurring
numberOfOccurringStrategies = len(occurringStrategiesNames)

# The current welfare matrix
currentWelfare = np.zeros((N, N), float)

# last action
if display_config.showLastActionMatrix:
    lastAction = np.zeros((3 * N, 3 * N), int) - 5
    for x in xrange(N):
        for y in xrange(N):
            lastAction[3 * x + 1, 3 * y + 1] = 5


def main():
    import gui

    ui = gui.PlotUI()

    # store config and initialize config.foldername
    config.store_configuration(ui.strategiesLabels)

    # initialize statistic storage
    statistics.prepareStoreStats(config.foldername)

    # run the simulation
    ui.main(simulation)


def simulation(ui):
    startEpochSeconds = time.time()
    print("Starting [" + str(time.asctime()) + "]")

    ui.refreshUI(0)

    # Let's play
    init_reputation()

    # initial refresh of UI, also stores pictures of initialization state
    ui.refreshUI(0)

    global iteration
    iteration = 0

    # MAIN LOOP
    steps = 0
    for iteration in xrange(M):
        if steps >= display_config.stepsBetweenRefresh:
            status = (
                "Iteration "
                + str(iteration)
                + " of "
                + str(M)
                + " ("
                + ("%f" % (100.0 * iteration / M))
                + "%)"
            )
            print(status)

            # reset step counter
            steps = 0

            # compute statistics if necessary
            if display_config.showStatsInSecondRow or config.storeStats:
                statistics.updateCurrentStatistics(iteration)

            # refresh UI and store images
            ui.refreshUI(iteration)

            # Give we_should_terminate a chance to run, even if no strategies change
            if iteration > 1000 and we_should_terminate():
                break

        # actual work: one iteration of the simulation
        changed = duel_with_strategy_update()
        if (
            display_config.steps_between_refresh_mode
            == display_config.numberOfIterations
            or changed
        ):
            steps += 1
        if changed and we_should_terminate():
            break

    # FINISHED SIMULATION

    # Store stats, finalize
    if config.storeStats:
        statistics.updateCurrentStatistics(iteration)
        statistics.closeStatsFiles()

    # Refresh and store images one last time
    ui.refreshUI(iteration)
    ui.signalDone()

    print("Done! [" + str(time.asctime()) + "]")
    print("      Took " + str(time.time() - startEpochSeconds) + "s")


def init_reputation():
    if not config.disableReputationInitializationRounds:
        # "Initialize" reputation by playing a few rounds without strategy updates
        if config.repInitMode == config.repInitModeGlobal:
            for _ in xrange(config.numberOfReputationInitializationRounds):
                # random (non-local) pairs
                p1 = choose_one_random_player()
                p2 = choose_one_random_player_except(p1)
                duel_without_strategy_update(p1, p2)
        elif config.repInitMode == config.repInitModeLocal:
            for _ in xrange(config.numberOfReputationInitializationRounds):
                # rep-init with local pairs only. (Introduces good AllDs!)
                p1 = choose_one_random_player()
                p1Neighbors = get_neighbors(p1)
                p2 = duelSelectionRandom.choice(p1Neighbors)
                duel_without_strategy_update(p1, p2)
        else:
            print("Missing/unhandled reputation init mode!")
            print(args)
            sys.exit(1)

        print('"Initialized" reputation, starting real game')


def we_should_terminate():
    aliveStrategies = {}
    for i in xrange(N):
        for j in xrange(N):
            aliveStrategies[strategies[i, j]] = True
    if config.terminateWhenOneStrategyDied:
        if len(aliveStrategies) < numberOfOccurringStrategies:
            print("One strategy died, stopping simulation!")
            return True
    if config.terminateWhenOnlyOneStrategyLeft:
        if len(aliveStrategies) <= 1:
            print("All but one strategies died, stopping simulation!")
            return True
    if config.terminateWhenDiscReachesBoundary:
        allD = games_and_strategies.allDefect
        allC = games_and_strategies.allCooperate
        reached = False
        reached = reached or np.any(
            (strategies[0, :] != allD) * (strategies[0, :] != allC)
        )
        reached = reached or np.any(
            (strategies[N - 1, :] != allD) * (strategies[N - 1, :] != allC)
        )
        reached = reached or np.any(
            (strategies[:, 0] != allD) * (strategies[:, 0] != allC)
        )
        reached = reached or np.any(
            (strategies[:, N - 1] != allD) * (strategies[:, N - 1] != allC)
        )
        if reached:
            print('Discriminators reached the "boundary" of the world, terminating ...')
            return True
    if config.terminateWhenAllCReachesBoundary:
        allC = games_and_strategies.allCooperate
        reached = False
        reached = reached or np.any(strategies[0, :] == allC)
        reached = reached or np.any(strategies[N - 1, :] == allC)
        reached = reached or np.any(strategies[:, 0] == allC)
        reached = reached or np.any(strategies[:, N - 1] == allC)
        if reached:
            print('allCs reached the "boundary" of the world, terminating ...')
            return True
    if config.terminateWhenRepConstant:
        guiRep = reputation[display_config.guiMoral]
        repConstant = np.all(guiRep[:] == guiRep[0, 0])
        if repConstant:
            print(
                "Reputation for "
                + morals.moralNames[display_config.guiMoral]
                + " is constant, terminating ..."
            )
            return True
    return False


def duel_without_strategy_update(player1, player2):
    # Determine their mixed strategy as probs to play pure strategy 0
    strategy1 = strategies[player1]
    strategy2 = strategies[player2]
    moral1 = strategyMoral[strategy1]
    moral2 = strategyMoral[strategy2]

    a1 = games_and_strategies.action(
        strategy1, get_reputation(moral1, player2, player1)
    )
    a2 = games_and_strategies.action(
        strategy2, get_reputation(moral2, player1, player2)
    )

    # Reputation update
    # has to be done for all morals
    repsToSet = []
    global repInitPolarizationSeed
    for moral in occurringMorals:
        oldRep1 = get_reputation(moral, player1, player2)
        oldRep2 = get_reputation(moral, player2, player1)

        # Use artificial polarized reputation in very first duel
        if repInitPolarizationSeed:
            oldRep1 = 0 if moral in morals.polarizationSeedScepticMorals else 1

        repsToSet.append(
            (
                moral,
                player1,
                morals.newReputation[moral](player1, moral, oldRep1, oldRep2, a1),
            )
        )
        repsToSet.append(
            (
                moral,
                player2,
                morals.newReputation[moral](player2, moral, oldRep2, oldRep1, a2),
            )
        )

    repInitPolarizationSeed = False

    for x, y, z in repsToSet:
        set_reputation(x, y, z)


# refers to https://www.ibr.cs.tu-bs.de/trac/algogame/wiki/RepEvolST - Rot-Blau Nachbau
# Variant (a): Replicator Updating with one neighbor
def duel_with_strategy_update():
    # choose focal and neighbor
    focal = choose_one_random_player()
    focalsNeighbors = get_neighbors(focal)
    chosen = duelSelectionRandom.choice(focalsNeighbors)
    chosenNeighbors = get_neighbors(chosen)

    # Determine payoff
    focalActions = dict(
        [(nn, get_action_for_player1(focal, nn)) for nn in focalsNeighbors]
    )
    chosenActions = dict(
        [(nn, get_action_for_player1(chosen, nn)) for nn in chosenNeighbors]
    )
    vsFocalActions = dict(
        [(nn, get_action_for_player1(nn, focal)) for nn in focalsNeighbors]
    )
    vsChosenActions = dict(
        [(nn, get_action_for_player1(nn, chosen)) for nn in chosenNeighbors]
    )
    focalPayoff = sum([get_payoff_for_player1(focal, nn) for nn in focalsNeighbors])
    chosenPayoff = sum([get_payoff_for_player1(chosen, nn) for nn in chosenNeighbors])

    # Store actions in lastAction
    if display_config.showLastActionMatrix:
        for neighbor in focalsNeighbors:
            store_last_action(focal, neighbor, focalActions[neighbor])
            store_last_action(neighbor, focal, vsFocalActions[neighbor])
        for neighbor in chosenNeighbors:
            store_last_action(chosen, neighbor, chosenActions[neighbor])
            store_last_action(neighbor, chosen, vsChosenActions[neighbor])

    # (Potential) strategy update
    changed = semideterministic_replicator_update(
        focal, chosen, focalPayoff, chosenPayoff
    )

    # do updates in random order
    duelSelectionRandom.shuffle(focalsNeighbors)
    duelSelectionRandom.shuffle(chosenNeighbors)

    # with a certain probability insert heaven/hell players into focalsNeighbors and chosenNeighbors
    if config.supernaturalMode:
        if config.heavenHellTogether:
            focalcontact_heaven = bernoulli(
                config.heavenContactProbFocal, duelSelectionRandom
            )
            focalcontact_hell = focalcontact_heaven
            chosencontact_heaven = bernoulli(
                config.heavenContactProbChosen, duelSelectionRandom
            )
            chosencontact_hell = chosencontact_heaven
        else:
            focalcontact_heaven = bernoulli(
                config.heavenContactProbFocal, duelSelectionRandom
            )
            focalcontact_hell = bernoulli(
                config.hellContactProbFocal, duelSelectionRandom
            )
            chosencontact_heaven = bernoulli(
                config.heavenContactProbChosen, duelSelectionRandom
            )
            chosencontact_hell = bernoulli(
                config.hellContactProbChosen, duelSelectionRandom
            )

        if focalcontact_heaven == 1:
            focalsNeighbors.append(HEAVEN)
            focalActions[HEAVEN] = games_and_strategies.action(strategies[focal], 1)
        if focalcontact_hell == 1:
            focalsNeighbors.append(HELL)
            focalActions[HELL] = games_and_strategies.action(strategies[focal], 0)

        if chosencontact_heaven == 1:
            chosenNeighbors.append(HEAVEN)
            chosenActions[HEAVEN] = games_and_strategies.action(strategies[chosen], 1)
        if chosencontact_hell == 1:
            chosenNeighbors.append(HELL)
            chosenActions[HELL] = games_and_strategies.action(strategies[chosen], 0)

    repsToSet = []
    safedirepUpdatesToSet = []

    # TODO: update mode - make it possible to update all neighbors' reputation
    # reputation update: again 'simulate' the played duels
    global repInitPolarizationSeed
    for moral in occurringMorals:
        focalRep = get_reputation(moral, focal, chosen)
        chosenRep = get_reputation(moral, chosen, focal)

        # update reputation for focal
        for neighbor in focalsNeighbors:
            focalsAction = focalActions[neighbor]
            focalRep = morals.newReputation[moral](
                focal,
                moral,
                focalRep,
                get_reputation(moral, neighbor, focal),
                focalsAction,
            )
            if moral in safedirep.againstPlayerBits:
                if neighbor not in [HEAVEN, HELL, polarizingPlayer]:
                    neighborsAction = vsFocalActions[neighbor]
                    safedirepUpdatesToSet.append((moral, neighbor, focal, focalsAction))
                    safedirepUpdatesToSet.append(
                        (moral, focal, neighbor, neighborsAction)
                    )

        # update reputation for chosen
        for neighbor in chosenNeighbors:
            chosenAction = chosenActions[neighbor]
            chosenRep = morals.newReputation[moral](
                chosen,
                moral,
                chosenRep,
                get_reputation(moral, neighbor, chosen),
                chosenAction,
            )
            if moral in safedirep.againstPlayerBits:
                if neighbor not in [HEAVEN, HELL, polarizingPlayer]:
                    neighborsAction = vsChosenActions[neighbor]
                    safedirepUpdatesToSet.append(
                        (moral, neighbor, chosen, chosenAction)
                    )
                    safedirepUpdatesToSet.append(
                        (moral, chosen, neighbor, neighborsAction)
                    )

        repsToSet.append((moral, focal, focalRep))
        repsToSet.append((moral, chosen, chosenRep))

    # actually perform the updates
    for moral, focal, newRep in repsToSet:
        set_reputation(moral, focal, newRep)
    for moral, victim, actor, action in safedirepUpdatesToSet:
        safedirep.store_action(moral, victim, actor, action)

    return changed


def semideterministic_replicator_update(focal, chosen, focalPayoff, chosenPayoff):
    diff = chosenPayoff - focalPayoff
    if config.deterministicStrategyUpdates:
        probForChosen = 0.0 if diff <= 0 else 1.0
    else:
        probForChosen = (0 if diff <= 0 else diff) / replicatorUpdateMaxScore
    if probForChosen <= 0:
        return False
    chosenMayReplace = bernoulli(probForChosen, duelSelectionRandom)
    if chosenMayReplace == 0:
        return False
    # Takeover!
    changed = strategies[chosen] != strategies[focal]
    strategies[focal] = strategies[chosen]
    return changed


def neighbor_offset(player, neighbor):
    diffx = neighbor[0] - player[0]
    diffy = neighbor[1] - player[1]
    if diffx > 1:  # player must be in top row
        diffx = -1
    elif diffx < -1:  # player must be in bottom row
        diffx = 1
    if diffy > 1:  # player must be in left column
        diffy = -1
    elif diffy < -1:  # player must be in right column
        diffy = 1
    return (diffx, diffy)


def neighbor_index(player, neighbor):
    return neighbor_offsets_index[neighbor_offset(player, neighbor)]


def store_last_action(actor, neighbor, action):
    if display_config.showLastActionMatrix:
        offset = neighbor_offset(actor, neighbor)
        x = 3 * actor[0] + 1 + offset[0]
        y = 3 * actor[1] + 1 + offset[1]
        lastAction[x, y] = action


def get_neighbors(focal):
    return [((focal[0] + x) % N, (focal[1] + y) % N) for (x, y) in neighbor_offsets]


def get_action_for_player1(player1, player2):
    strategy = strategies[player1]
    moral = games_and_strategies.strategyMoral[strategy]
    return games_and_strategies.action(
        strategy, get_reputation(moral, player2, player1)
    )


def get_payoff_for_player1(player1, player2):
    a1 = get_action_for_player1(player1, player2)
    a2 = get_action_for_player1(player2, player1)
    return payoffs[a1, a2]


def get_reputation(moral, judged, judging):
    global polarizingPlayer

    # heaven & hell are globally seen as good/evil
    if judged == HELL:
        return 0
    if judged == HEAVEN:
        return 1

    # the polarizing player is seen as bad by some and good by others
    if judged == polarizingPlayer:
        return 0 if moral in morals.polarizationSeedScepticMorals else 1

    if moral == morals.smartMafia:
        return smart_mafia.get_reputation(
            reputation[moral][judging], reputation[moral][judged]
        )

    # handle morals with direct reciprocity
    if moral in safedirep.againstPlayerBits:
        # direct reciprocity only changes things if the target is globally bad
        if reputation[moral][judged] < 0.5:
            lastAction = safedirep.againstPlayerBits[moral][
                judging[0], judging[1], neighbor_index(judging, judged)
            ]

            # have we seen her before?
            if lastAction != -1:
                return 1 if lastAction == games_and_strategies.cooperate else 0

    # otherwise, use normal reputation
    return reputation[moral][judged]


def set_reputation(moral, player, newReputation):
    reputation[moral][player] = newReputation

    # update safedirep visualization
    if moral in safedirep.againstPlayerBits:
        # Store global view on player in matrix
        x = 3 * player[0] + 1
        y = 3 * player[1] + 1
        safedirep.visualMatrix[moral][x, y] = newReputation


def choose_one_random_player():
    return (
        duelSelectionRandom.randint(0, N - 1),
        duelSelectionRandom.randint(0, N - 1),
    )


def choose_one_random_player_except(exceptions):
    if not isinstance(exceptions, list):
        exceptions = [exceptions]
    player = choose_one_random_player()
    while player in exceptions:
        player = choose_one_random_player()
    return player


def score_without_updates(player):
    neighbors = get_neighbors(player)
    return sum([get_payoff_for_player1(player, nn) for nn in neighbors])


def compute_welfare():
    welfare = np.zeros((N, N), float)

    for x in xrange(N):
        for y in xrange(N):
            welfare[x, y] = score_without_updates((x, y)) / replicatorUpdateMaxScore

    return welfare


def update_current_welfare():
    global currentWelfare
    currentWelfare = compute_welfare()


def avg_global_welfare():
    update_current_welfare()
    return np.sum(currentWelfare, axis=(0, 1)) / (N * N)
