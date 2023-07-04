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

from cmdline_args import args
import strategies


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
