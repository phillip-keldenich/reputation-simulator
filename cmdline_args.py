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

import argparse
import sys
from cmdline_parser import MyFormatter, PolarizingPlayerAction


argParser = argparse.ArgumentParser(
    description="RepEvol Simulator", formatter_class=MyFormatter
)

# Game Settings
argParser.add_argument(
    "-g",
    "--game",
    default="PD",
    choices=("PD", "SD"),
    help="Which duel game to use (Prisoners Dilemma (PD) or Snow Drift (SD), default: %(default)s)",
)
argParser.add_argument(
    "-U",
    "--U",
    default=0.6,
    type=float,
    metavar="float",
    help="The parameter of the game, must be in range [0,1] (default: %(default)s)",
)

# Simulation settings
argParser.add_argument(
    "-M",
    "--M",
    default=10000001,
    type=int,
    metavar="int",
    help="The number of iterations to simulate (default: %(default)s)",
)
argParser.add_argument(
    "--terminate-if-disc-reaches-boundary",
    default=False,
    const=True,
    action="store_const",
    help="Terminates the simulation as soon as the first "
    + 'discriminating player touches the "boundary" of the world. '
    + "(Yes, a torus does not have boundaries, but this is just a "
    + "computer scientist's hack ...)",
)
argParser.add_argument(
    "--terminate-if-allC-reaches-boundary",
    default=False,
    const=True,
    action="store_const",
    help="Terminates the simulation as soon as the first "
    + 'allC player touches the "boundary" of the world.',
)
argParser.add_argument(
    "--seed",
    default=None,
    type=int,
    help="Initialize random number generator with the given seed. "
    + "The default is to take current time, but for reproducibility "
    + "you might prefer setting some constant.",
)

# Reputation update mode
argParser.add_argument(
    "--rep-update-mode",
    choices=["focal+chosen", "all"],
    default="focal+chosen",
    help="Determines which players have their reputation updated after a duel." + ""
    '"focal+chosen" (default) means that only focal and chosen have their reputation updated,'
    + ""
    'whereas "all" also updates the reputation of the other neighbors.',
)

# Deterministic updates
argParser.add_argument(
    "--deterministic-strategy-updates",
    default=False,
    const=True,
    action="store_const",
    help="Always adopt the strategy of the winner instead of a probability-based update.",
)

# Torus settings & Initial State
argParser.add_argument(
    "-N",
    "--N",
    default=80,
    type=int,
    metavar="int",
    action=PolarizingPlayerAction,
    help="The side length of the square lattice (default: %(default)s)",
)

import strategy_init

argParser.add_argument(
    "-I",
    "--initial-strategies",
    choices=list(strategy_init.scenarios),
    default="allD_ClusterSaferep",
    help="The initial assignment of strategies.  (default: %(default)s)"
    + "Can be any of "
    + 'the following predefined populations or "custom". '
    + 'For "custom" you have to provide a script to '
    + "initialize strategies matrix via --initial-strategies-script<>"
    + "Predefined populations:<>"
    + "  *  all[C/D]_ClusterX: initialize with all[C/D], add sxs cluster X<>"
    + "  *  allD_CircleMafia: initialize with allD, <>"
    + "add mafia circle with radius s in the middle<>"
    + "  *  halfAllD_halfAllC_ClusterX: initialize upper half with allC, "
    + "lower half with allD, then add sxs cluster X",
)

# HEAVEN/HELL settings
argParser.add_argument(
    "--hell-prob-focal",
    default=None,
    type=float,
    help="The probability that focal makes contact with the absolute evil (HELL)<>" + ""
    "(independently for every played duel focal--chosen)",
)
argParser.add_argument(
    "--hell-prob-chosen",
    default=None,
    type=float,
    help="The probability that focal makes contact with the absolute evil (HELL)<>" + ""
    "(independently for every played duel focal--chosen)",
)
argParser.add_argument(
    "--heaven-prob-focal",
    default=None,
    type=float,
    help="The probability that focal makes contact with the absolute good (HEAVEN)<>"
    + ""
    "(independently for every played duel focal--chosen)",
)
argParser.add_argument(
    "--heaven-prob-chosen",
    default=None,
    type=float,
    help="The probability that chosen makes contact with the absolute good (HEAVEN)<>"
    + ""
    "(independently for every played duel focal--chosen)",
)
argParser.add_argument(
    "--heaven-prob",
    default=0,
    type=float,
    help="The probability that players make constact with HEAVEN player."
    + "The specific flags --heaven-prob-[focal/chosen] take precedence.",
)
argParser.add_argument(
    "--hell-prob",
    default=0,
    type=float,
    help="The probability that players make constact with HELL player."
    + "The specific flags --hell-prob-[focal/chosen] take precedence.",
)

# Initialization
argParser.add_argument(
    "-s",
    "--s",
    default=5,
    type=int,
    metavar="int",
    help="The side length of the initial square of cooperators "
    + "(s<N), only active if initial strategies uses square cluster"
    + " (default: %(default)s)",
)
argParser.add_argument(
    "-T",
    "--initial-strategies-script",
    type=argparse.FileType("r"),
    default=None,
    help="If you give set --initial-strategies=custom, you must "
    + "provide an initializing script here. For an example "
    + 'of such script, see "initial-strategies-demo.py"',
)
argParser.add_argument(
    "--rep-init-rounds",
    default=None,
    type=int,
    metavar="int",
    help="Number of reputation initialization duels without strategy<> "
    + "updates, before actual simulation starts.<> "
    + "Default: 10*N*N",
)
argParser.add_argument(
    "--rep-init-type",
    choices=["local", "global"],
    default="global",
    help="Defines how the random duels for reputation initialization<> "
    + 'are drawn: "local" means we draw a random player and one of its<> '
    + 'neighbors; "global" means we draw two (distinct) players independently. '
    + "(default: %(default)s)",
)
argParser.add_argument(
    "--no-rep-init",
    default=False,
    const=True,
    action="store_const",
    help="Skip initial rounds of reputation building without strategy<> "
    + "propagation.",
)
argParser.add_argument(
    "-p",
    "--prob-for-init",
    type=float,
    default=0.5,
    metavar="float",
    help="Parameter for initial strategy populations using iid distributions.",
)
argParser.add_argument(
    "--polarization-seed",
    action="store_true",
    help="In the very first reputation initialization duel, <>" + ""
    "a difference in observed old reputation is enforced, <>"
    + "which can serve as a seed of polarization of reputation.",
)
argParser.add_argument(
    "--polarizing-player",
    default=None,
    action=PolarizingPlayerAction,
    help='Define a polarizing player (for example "(0,0)") who will be constantly evil for '
    + "some morals and constantly good for others.",
)

# Display/Storage Settings
argParser.add_argument(
    "-r",
    "--steps-between-refresh",
    default=1000,
    type=int,
    metavar="int",
    help="The number of iterations between GUI refreshes (default: %(default)s)",
)
argParser.add_argument(
    "-R",
    "--refresh-mode",
    choices=["iterations", "pixels"],
    default="iterations",
    help="Define used progress measure: total number of iterations"
    + " or number of changed pixels. (default: %(default)s)",
)
argParser.add_argument(
    "--no-stats",
    default=False,
    const=True,
    action="store_const",
    help="Disable statistics written to CSV file.",
)
argParser.add_argument(
    "--welfare", action="store_true", help="Enable tracking of global welfare."
)
argParser.add_argument(
    "-o",
    "--output-folder",
    default=None,
    metavar="outputFolder",
    help="The name of the folder all results are written to. "
    + "Default is current date and time.<> "
    + "Note that RepEvol will exit if the given folder already exists.",
)
argParser.add_argument(
    "-c",
    "--strategy-colors",
    default="all-different",
    choices=["all-different", "all-disc-yellow", "nature"],
    help="Set the color map used for strategies.",
)
argParser.add_argument(
    "--no-morals-diff",
    default=False,
    const=True,
    action="store_const",
    help="Store a matrix of differences between the first two interesting " + "morals.",
)
argParser.add_argument(
    "--gui-backend",
    default=None,
    metavar="gui_backend",
    help="Which GUI backend to use for matplotlib.",
)
argParser.add_argument(
    "--store-whole-pictures",
    default=False,
    const=True,
    action="store_const",
    help="Store the content of the GUI as images.",
)

# GUI Settings
argParser.add_argument(
    "--first-row",
    default="diffMatrices",
    choices=["matrices", "diffMatrices", "strategyStats"],
    help="What is shown in the first row of the GUI. (default: %(default)s)",
)
argParser.add_argument(
    "--no-gui-stats",
    default=False,
    const=True,
    action="store_const",
    help="Disable the statistics in the second row.",
)
argParser.add_argument(
    "--no-gui",
    default=False,
    const=True,
    action="store_const",
    help="Completely disable the GUI.",
)
argParser.add_argument(
    "--gui-moral",
    default="saferep",
    metavar="moralName",
    help="The name of the moral to show in GUI.",
)
argParser.add_argument(
    "--show-last-actions",
    action="store_true",
    help="Show and store the lastAction 3Nx3N matrix.",
)

argParser.add_argument(
    "--heaven-hell-together",
    default=False,
    const=True,
    action="store_const",
    help="Only perform one random draw to determine whether both heaven and hell participate in a duel (or neither).",
)


args = argParser.parse_args()


def get_commandline():
    return " ".join(sys.argv[1:])
