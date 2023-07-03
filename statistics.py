#   _____ _        _   _     _   _
#  / ____| |      | | (_)   | | (_)
# | (___ | |_ __ _| |_ _ ___| |_ _  ___ ___
#  \___ \| __/ _` | __| / __| __| |/ __/ __|
#  ____) | |_ (_| | |_| \__ \ |_| | (__\__ \
# |_____/ \__\__,_|\__|_|___/\__|_|\___|___/
#

import os
import numpy as np
from math import *

from misc_globals import strategies, reputation
from misc_globals import occurringInterestingMorals, occurringStrategiesNames
import morals
import config
import games_and_strategies

# current is a map from strategies to map of statistics for this strategy.
# For each strategy there are the fields defined below as 'Stats per strategy'.
# The field reputationStats is itself a map containing stats for all morals.
current = {}


# Stats per strategy
iterations = 0
numberOfPlayers = 1
reputationStats = 2
welfareStats = 8

# Stats per strategy & moral
perMoralMean = 3
perMoralStdevAbove = 4
perMoralStdevBelow = 5
perMoralNGood = 6
perMoralNBad = 7

# Headers of columns in CSV file
csvHeader = {
    iterations: "Iteration",
    numberOfPlayers: "#players",
    perMoralMean: " reputation mean",
    perMoralStdevAbove: " reputation stdev above mean",
    perMoralStdevBelow: " reputation stdev below mean",
    perMoralNGood: " reputation #players >= 0.5 (good)",
    perMoralNBad: " reputation #players < 0.5 (bad)",
    welfareStats: "avg. score (normalized to [0,1])",
}

# Open files for
csvFiles = {}
csvSep = ";"


def updateCurrentStatistics(iteration):
    """Compute the statistics for all strategies and all interesting morals,
    store the result in current. Additionally, store the stats in a CSV
    file if config.storeStats is true.
    """
    if config.welfareStatistics:
        from implementation import update_current_welfare

        update_current_welfare()

    for strategy in occurringStrategiesNames.keys():
        current[strategy] = computeStats(strategy)
        current[strategy][iterations] = iteration
    if config.storeStats:
        storeCurrentStats()


def strategy_counts():
    result = np.zeros(len(occurringStrategiesNames))
    index = 0
    for strategy in occurringStrategiesNames.keys():
        result[index] = current[strategy][numberOfPlayers]
        index += 1
    return result


def computeStats(strategy):
    sel = strategies == strategy
    n = np.sum(sel)
    repStats = {}
    for moral in occurringInterestingMorals:
        rep = reputation[moral]
        avgRep = float(np.sum(rep * sel)) / n if n > 0 else 0
        selRepAbove = sel * (rep >= avgRep)
        selRepBelow = sel * (rep <= avgRep)
        nRepAbove = np.sum(selRepAbove)
        nRepBelow = np.sum(selRepBelow)
        stdDevRepAbove = (
            sqrt(np.sum(((rep - avgRep) * selRepAbove) ** 2) / nRepAbove)
            if nRepAbove > 0
            else 0
        )
        stdDevRepBelow = (
            sqrt(np.sum(((rep - avgRep) * selRepBelow) ** 2) / nRepBelow)
            if nRepBelow > 0
            else 0
        )

        nGood = int(np.sum((((rep + 10) * sel) - 10) >= 0.5))
        nBad = int(np.sum((((rep - 10) * sel) + 10) < 0.5))

        repStats[moral] = {
            perMoralMean: avgRep,
            perMoralStdevAbove: stdDevRepAbove,
            perMoralStdevBelow: stdDevRepBelow,
            perMoralNGood: nGood,
            perMoralNBad: nBad,
        }

    res = {numberOfPlayers: n, reputationStats: repStats}

    if config.welfareStatistics:
        from implementation import currentWelfare

        res[welfareStats] = (np.sum(sel * currentWelfare) / n) if n > 0 else 0

    return res


def prepareStoreStats(foldername):
    if not config.storeStats:
        return
    for strategy in occurringStrategiesNames.keys():
        csvFile = open(
            foldername
            + os.sep
            + "stats-for-"
            + games_and_strategies.strategyName[strategy]
            + ".csv",
            "w",
        )
        csvFiles[strategy] = csvFile
        csvFile.write(csvHeader[iterations] + csvSep + csvHeader[numberOfPlayers])
        for moral in occurringInterestingMorals:
            name = morals.moralNames[moral]
            csvFile.write(
                csvSep
                + name
                + csvHeader[perMoralMean]
                + csvSep
                + name
                + csvHeader[perMoralStdevAbove]
                + csvSep
                + name
                + csvHeader[perMoralStdevBelow]
                + csvSep
                + name
                + csvHeader[perMoralNGood]
                + csvSep
                + name
                + csvHeader[perMoralNBad]
            )
        if config.welfareStatistics:
            csvFile.write(csvSep + csvHeader[welfareStats])
        csvFile.write(os.linesep)


def storeCurrentStats():
    if not config.storeStats:
        return
    for strategy in occurringStrategiesNames.keys():
        s = current[strategy]
        csvFile = csvFiles[strategy]
        csvFile.write(str(s[iterations]) + csvSep + str(s[numberOfPlayers]))
        for moral in occurringInterestingMorals:
            r = s[reputationStats][moral]
            csvFile.write(
                csvSep
                + str(r[perMoralMean])
                + csvSep
                + str(r[perMoralStdevAbove])
                + csvSep
                + str(r[perMoralStdevBelow])
                + csvSep
                + str(r[perMoralNGood])
                + csvSep
                + str(r[perMoralNBad])
            )
        if config.welfareStatistics:
            csvFile.write(csvSep + str(s[welfareStats]))
        csvFile.write(os.linesep)
        csvFile.flush()


def closeStatsFiles():
    if not config.storeStats:
        return
    for csvFile in csvFiles.values():
        csvFile.close()
