from cmdline_args import args
import strategies

# ___  _ ____ ___  _    ____ _   _    ____ ___  ___ _ ____ _  _ ____
# |  \ | [__  |__] |    |__|  \_/     |  | |__]  |  | |  | |\ | [__
# |__/ | ___] |    |___ |  |   |      |__| |     |  | |__| | \| ___]
#


# steps between refresh mode
numberOfIterations = "iterations"
changedPixels = "pixels"
steps_between_refresh_mode = args.refresh_mode

stepsBetweenRefresh = args.steps_between_refresh

# Size of main window in pixels
sizeOfMainWindow = (800, 800)
displayDPI = 72

# Options of what to show in the first row ...
matrices = "matrices"
perStrategyDetailedStats = "strategyStats"
matricesWithRepDiff = "diffMatrices"
# ... from which the active one can be chosen:
showInFirstRow = args.first_row


# store the whole picture  every stepsBetweenStoresImages steps
storeWholePictures = args.store_whole_pictures
outputDPI = 75
# store matrices as images every stepsBetweenStoresImages steps
storeMatrices = True

# Select strategy colors
strategyColor = strategies.strategyColorMap[args.strategy_colors]


# Moral to show reputation for in GUI
guiMoral = -1

# Disable GUI
completelyDisableGUI = args.no_gui

showStatsInSecondRow = not (args.no_gui_stats or args.no_gui)

showLastActionMatrix = not args.no_gui and args.show_last_actions

gui_backend = args.gui_backend
