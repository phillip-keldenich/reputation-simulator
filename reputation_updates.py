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

from misc_globals import strategies
from games_and_strategies import cooperate, defect, mafia, mafia2
import morals


# Trivial reputation update.
def amoral(me, moral, my_old_rep, her_old_rep, my_action):
    return 0


#  ___      ___     ___
# / __|__ _| __|___| _ \___ _ __
# \__ | _` | _|/ -_)   / -_) '_ \
# |___|__,_|_| \___|_|_\___| .__/
#                          |_|
def saferep(me, moral, my_old_rep, her_old_rep, my_action):
    if her_old_rep >= 0.5:
        morals.saferepAgainstGoodBits[moral][me] = my_action
    else:
        morals.saferepAgainstBadBits[moral][me] = my_action
    return (
        1
        if morals.saferepAgainstGoodBits[moral][me] == cooperate
        and morals.saferepAgainstBadBits[moral][me] == defect
        else 0
    )


#    _  __             _         _
#   | |/ /__ _ _ _  __| |___ _ _(_)
#   | ' </ _` | ' \/ _` / _ \ '_| |
#   |_|\_\__,_|_||_\__,_\___/_| |_|
#
def genericKandori(me, moral, my_old_rep, her_old_rep, my_action):
    compliant = (her_old_rep >= 0.5 and my_action == cooperate) or (
        her_old_rep < 0.5 and my_action == defect
    )
    history = morals.kandoriHistory[moral]
    if compliant:
        # increment state --> get "nearer to good"
        history[me] = min(0, history[me] + 1)
    else:
        # bad action --> back to "worst" state -T
        history[me] = -morals.kandoriPenaltyLoop[moral]
    return 1 if history[me] == 0 else 0


#  __  __       __ _
# |  \/  |__ _ / _(_)__ _
# | |\/| / _` |  _| / _` |
# |_|  |_\__,_|_| |_\__,_|
#
def neverBetrayTheFamily(me, moral, my_old_rep, her_old_rep, my_action):
    # no matter what you do and whom you met, all that counts is the family
    return 1 if strategies[me] == mafia else 0


def neverBetrayTheOtherFamily(me, moral, my_old_rep, her_old_rep, my_action):
    # no matter what you do and whom you met, all that counts is the family
    return 1 if strategies[me] == mafia2 else 0
