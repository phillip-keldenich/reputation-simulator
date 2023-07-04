"""
Created on Apr 12, 2017.
The sole purpose of this is to have the symbolic constants for the
strategies available without triggering the import/parsing of the command line.
This would then introduce nasty circular import problems.


@author: Phillip Keldenich
"""

# Strategy types for each player
# (plain constants / names for the indices)
allDefect = 1
allCooperate = 2
mafia = 3
saferep = 4
republicans = saferep
republicans2 = 5
democrats = 6
democrats2 = 7
kandori1 = 8
kandori2 = 9
kandori3 = 10
kandori8 = 11
kandori9 = 12
kandoriInitiallyGood = 13
safedirep = 14
safedirep2 = 15
smartMafia = 16
mafia2 = 17

# Define screen names for the strategies
strategyName = {
    allDefect: "AllD",
    mafia: "Mafia",
    saferep: "GandhiB",
    kandori1: "Kandori1",
    kandori2: "Kandori2",
    kandori3: "Kandori3",
    kandori8: "Kandori8",
    kandori9: "Kandori9",
    allCooperate: "AllC",
    democrats: "GandhiG",
    democrats2: "GandhiG2",
    republicans2: "GandhiB2",
    kandoriInitiallyGood: "Kandori(InitiallyGood)",
    safedirep: "Gandhi++",
    safedirep2: "Gandhi++2",
    smartMafia: "SmartMafia",
    mafia2: "Mafia2",
}

# Strategies for which to insert scenarios automatically, and their names
scenarioStrategyNames = {
    allDefect: "allD",
    allCooperate: "allC",
    saferep: "Gandhi",
    kandori1: "kandori1",
    kandori2: "kandori2",
    kandori3: "kandori3",
    kandori8: "kandori8",
    kandori9: "kandori9",
    democrats: "GandhiG",
    republicans: "GandhiB",
    kandoriInitiallyGood: "KandoriInitiallyGood",
    safedirep: "Gandhi++",
    smartMafia: "smartMafia",
}

# Define colors for the strategies
strategyColorMap = {
    "all-different": {
        allDefect: "r",
        mafia: "k",
        mafia2: "k",
        saferep: "#800000",
        kandori1: "#800080",
        kandori2: "#A64DA6",
        kandori3: "#8F00B2",
        kandori8: "#FF00FF",
        kandori9: "#FF80FF",
        allCooperate: "#3366FF",
        democrats: "#000099",
        democrats2: "#6666C2",
        republicans2: "#B36666",
        kandoriInitiallyGood: "#DBB8DB",
        safedirep: "#006600",
        safedirep2: "#66A366",
        smartMafia: "#FF6600",
    },
    "all-disc-yellow": {
        allDefect: "r",
        mafia: "k",
        mafia2: "k",
        saferep: "#FFFF00",
        kandori1: "#FFFF00",
        kandori2: "#FFFF00",
        kandori3: "#FFFF00",
        kandori8: "#FFFF00",
        kandori9: "#FFFF00",
        allCooperate: "b",
        democrats: "#FFFF00",
        democrats2: "#FFFF00",
        republicans2: "#FFFF00",
        kandoriInitiallyGood: "#FFFF00",
        safedirep: "#FFFF00",
        safedirep2: "#FFFF00",
        smartMafia: "#FF6600",
    },
    "nature": {
        allDefect: "#ff9900",
        allCooperate: "#9eff66",
        republicans: "#cc0000",
        republicans2: "#ff3333",
        democrats: "#000099",
        democrats2: "#800000",
        safedirep: "#9900cc",
        safedirep2: "#cc33ff",
        mafia: "#000000",
        mafia2: "#333333",
        smartMafia: "#666666",
	    kandori1: "#800080",
        kandori2: "#A64DA6",
        kandori3: "#8F00B2",
        kandori8: "#FF00FF",
        kandori9: "#FF80FF",
        kandoriInitiallyGood: "#DBB8DB",
    },
}

numberOfDifferentStrategies = len(strategyName.keys())

discriminatorStrategies = [
    kandori1,
    kandori2,
    kandori3,
    kandori8,
    kandori9,
    saferep,
    democrats,
    democrats2,
    republicans2,
    mafia,
    mafia2,
    kandoriInitiallyGood,
    safedirep,
    safedirep2,
    smartMafia,
]
