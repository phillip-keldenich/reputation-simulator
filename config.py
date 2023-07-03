import numpy as np
import display_config
from misc_globals import strategies, reputation, N
from misc_globals import occurringStrategiesNames, occurringStrategies
from misc_globals import occurringMorals, occurringInterestingMorals
from misc_globals import seed
import games_and_strategies
import morals
from cmdline_args import args, get_commandline
import sys

# python3 support - this works regardless of python version.
try:
    xrange
except NameError:
    xrange = range

#
#
#   _____             __ _                       _   _
#  / ____|           / _(_)                     | | (_)
# | |     ___  _ __ | |_ _  __ _ _   _ _ __ __ _| |_ _  ___  _ __
# | |    / _ \| '_ \|  _| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \
# | |____ (_) | | | | | | | (_| | |_| | | | (_| | |_| | (_) | | | |
#  \_____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|
#                           __/ |
#                          |___/
#

# The folder that we write images/statistics and configuration to
foldername = ""


# Stores the commandline to a file and initializes the foldername
def store_configuration(strategyLabels):
    import os
    from datetime import datetime
    from strategies import strategyName
    from games_and_strategies import payoffs

    global foldername

    if args.output_folder is None:
        timestamp = datetime.now()
        foldername = timestamp.strftime("%Y-%m-%d__%H-%M-%S.%f")
    else:
        foldername = args.output_folder

    print("Writing results to " + os.path.abspath(str(foldername)) + ".")
    if os.path.exists(foldername):
        print("Folder " + str(foldername) + " already exists! Exiting.")
        sys.exit(2)

    os.makedirs(foldername)
    n = os.linesep

    occurringMoralNames = {}
    for moral in occurringMorals:
        occurringMoralNames[moral] = morals.moralNames[moral]

    keyLen = 40
    cmdlineArgs = args.__dict__

    # Store the used functions in textfile
    configfile = open(foldername + os.sep + "config.txt", "w")
    configfile.write("Configuration" + n + n)
    configfile.write("Call parameters: " + n + "\t" + get_commandline() + n + n)
    configfile.write("Parameters:" + n)

    # Write cmdline args
    for arg in sorted(cmdlineArgs.keys()):
        configfile.write(str(arg).ljust(keyLen) + " = " + str(cmdlineArgs[arg]) + n)

    configfile.write(n + n + "Hardcoded Parameters:" + n)
    configfile.write("Game Matrix: " + n + str(payoffs) + n)
    configfile.write("random seed".ljust(keyLen) + " = " + str(seed) + n)
    configfile.write(n + n + "Environment:" + n)
    configfile.write(
        "occurring strategies".ljust(keyLen) + " = " + str(strategyLabels) + n
    )
    configfile.write(
        "occurring morals".ljust(keyLen) + " = " + str(occurringMoralNames.values()) + n
    )
    configfile.write(n)
    configfile.write(
        "all implemented strategies".ljust(keyLen) + " = " + str(strategyName) + n
    )

    configfile.close()

    return foldername


# _ _  _ _ ___ _ ____ _       ____ ___ ____ ___ ____
# | |\ | |  |  | |__| |       [__   |  |__|  |  |___
# | | \| |  |  | |  | |___    ___]  |  |  |  |  |___
#

import strategy_init

initializeStrategies = strategy_init.scenarios[args.initial_strategies]
if initializeStrategies is None:
    print("Your initial strategies have not been implemented yet!")
    exit(17)
else:
    initializeStrategies()

disableReputationInitializationRounds = args.no_rep_init
if args.rep_init_rounds is None:
    numberOfReputationInitializationRounds = 10 * N * N
else:
    numberOfReputationInitializationRounds = args.rep_init_rounds

# ____ _  _ ___     ____ ____    _ _  _ _ ___ _ ____ _       ____ ___ ____ ___ ____
# |___ |\ | |  \    |  | |___    | |\ | |  |  | |__| |       [__   |  |__|  |  |___
# |___ | \| |__/    |__| |       | | \| |  |  | |  | |___    ___]  |  |  |  |  |___
#
# DO NOT CHANGE STRATEGIES AFTER THIS LINE!!
#


# Compute occurring strategies
# find actually occurring strategies
for i in xrange(N):
    for j in xrange(N):
        occurringStrategies.add(strategies[i, j])
        occurringStrategiesNames[strategies[i, j]] = games_and_strategies.strategyName[
            strategies[i, j]
        ]

for strategy in occurringStrategiesNames.keys():
    moral = games_and_strategies.strategyMoral[strategy]
    occurringMorals.add(moral)
    if not moral in morals.uninterestingMorals:
        occurringInterestingMorals.add(moral)

# Set guiMoral to the first occurring one, if it does not occur itself
display_config.guiMoral = morals.moralByName(args.gui_moral)
guiMoralFallback = -1
if display_config.guiMoral not in occurringMorals:
    for someMoral in occurringMorals:
        guiMoralFallback = someMoral
        if someMoral in morals.uninterestingMorals:
            continue
        if display_config.guiMoral == -1:
            print(
                "WARNING: you gave me an invalid moralName as guiMoral!"
                + " Showing "
                + morals.moralNames[someMoral]
                + " in GUI."
            )
        else:
            print(
                "WARNING showing "
                + morals.moralNames[someMoral]
                + " in GUI instead of "
                + morals.moralNames[display_config.guiMoral]
                + "."
            )
        display_config.guiMoral = someMoral
        break
    # maybe, there are no interesting morals
    if display_config.guiMoral not in occurringMorals:
        display_config.guiMoral = guiMoralFallback
occurringInterestingMorals.add(display_config.guiMoral)


storeMoralDiff = not args.no_morals_diff
diffMorals = sorted(occurringInterestingMorals)
for moral in occurringMorals:
    if moral not in diffMorals and not moral == morals.dontCare:
        diffMorals += [moral]
if len(diffMorals) < 2:
    storeMoralDiff = False
    if display_config.showInFirstRow == display_config.matricesWithRepDiff:
        display_config.showInFirstRow = display_config.matrices

# init reputation
for moral in occurringMorals:
    reputation[moral] = morals.initMoral[moral](moral, strategies)


repInitModeLocal = 0
repInitModeGlobal = 1
repInitMode = repInitModeLocal if args.rep_init_type == "local" else repInitModeGlobal


# Re-initialize numpy random, such that number of uses for initial state creation
# does not affect uses in implementation
np.random.seed(seed + 42)


# _  _ ____ ____ _  _ ____ _  _    ____ _  _ ___     _  _ ____ _    _
# |__| |___ |__| |  | |___ |\ |    |__| |\ | |  \    |__| |___ |    |
# |  | |___ |  |  \/  |___ | \|    |  | | \| |__/    |  | |___ |___ |___
#
heavenHellTogether = args.heaven_hell_together
heavenContactProbFocal = args.heaven_prob
heavenContactProbChosen = args.heaven_prob
hellContactProbFocal = args.hell_prob
hellContactProbChosen = args.hell_prob
if args.heaven_prob_focal is not None:
    heavenContactProbFocal = args.heaven_prob_focal
if args.heaven_prob_chosen is not None:
    heavenContactProbChosen = args.heaven_prob_chosen
if args.hell_prob_focal is not None:
    hellContactProbFocal = args.hell_prob_focal
if args.hell_prob_chosen is not None:
    hellContactProbChosen = args.hell_prob_chosen
supernaturalMode = (
    heavenContactProbChosen > 0
    or heavenContactProbFocal > 0
    or hellContactProbChosen > 0
    or hellContactProbFocal > 0
)

# ____ ____ ____ _    _   _    ___ ____ ____ _  _ _ _  _ ____ ___ _ ____ _  _
# |___ |__| |__/ |     \_/      |  |___ |__/ |\/| | |\ | |__|  |  | |  | |\ |
# |___ |  | |  \ |___   |       |  |___ |  \ |  | | | \| |  |  |  | |__| | \|
#

terminateWhenOneStrategyDied = False
terminateWhenOnlyOneStrategyLeft = True
terminateWhenDiscReachesBoundary = args.terminate_if_disc_reaches_boundary
terminateWhenAllCReachesBoundary = args.terminate_if_allC_reaches_boundary
terminateWhenRepConstant = False


# ____ ___ ____ ___ _ ____ ___ _ ____ ____
# [__   |  |__|  |  | [__   |  | |    [__
# ___]  |  |  |  |  | ___]  |  | |___ ___]
#

storeStats = not args.no_stats
welfareStatistics = args.welfare

# Reputation update mode
repUpdateFocalChosen = 0
repUpdateAll = 1
repUpdateMode = repUpdateAll if args.rep_update_mode == "all" else repUpdateFocalChosen

# Strategy update mode
deterministicStrategyUpdates = args.deterministic_strategy_updates

# Polarizing player
polarizingPlayer = args.polarizing_player
