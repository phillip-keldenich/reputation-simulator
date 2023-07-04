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


import morals
import numpy as np

againstPlayerBits = {}
visualMatrix = {}

initialAgainstPlayerAction = {
    morals.safedirep: -1,
    morals.safedirep2: -1,
}


def initSafedirep(moral, strategies):
    from config import N

    againstPlayerBits[moral] = (
        np.ones((N, N, 8), int) * initialAgainstPlayerAction[moral]
    )
    visualMatrix[moral] = np.zeros((3 * N, 3 * N), int) - 5
    return morals.initSaferep(moral, strategies)


def store_action(moral, victim, actor, action):
    from implementation import neighbor_index, neighbor_offset
    from games_and_strategies import cooperate

    # store for the actual game
    nb = neighbor_index(victim, actor)
    againstPlayerBits[moral][victim[0], victim[1], nb] = action

    # store for the visualization
    off = neighbor_offset(actor, victim)
    x = 3 * actor[0] + 1 + off[0]
    y = 3 * actor[1] + 1 + off[1]
    visualMatrix[moral][x, y] = 2 if action == cooperate else 3
