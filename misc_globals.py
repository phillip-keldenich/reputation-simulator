import numpy as np
import random
from cmdline_args import args
from math import ceil, log10

# Populations size (side length)
N = args.N  # use command line argument
# Number of iterations
M = args.M  # use command line argument

# The number of digits in M in decimal notation
numberOfDigitsInM = str(int(ceil(log10(M))))

# Define matrices here
strategies = np.zeros((N, N), int)
reputation = {}  # initialized in config

# constant neighbor offsets
neighbor_offsets = [
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [0, -1],
    [0, 1],
    [1, -1],
    [1, 0],
    [1, 1],
]
neighbor_offsets_index = {
    (-1, -1): 0,
    (-1, 0): 1,
    (-1, 1): 2,
    (0, -1): 3,
    (0, 1): 4,
    (1, -1): 5,
    (1, 0): 6,
    (1, 1): 7,
}


#   ____ ____ _  _ ___  ____ _  _    _  _ _  _ _  _ ___  ____ ____ ____
#   |__/ |__| |\ | |  \ |  | |\/|    |\ | |  | |\/| |__] |___ |__/ [__
#   |  \ |  | | \| |__/ |__| |  |    | \| |__| |  | |__] |___ |  \ ___]
#

# Helper functions


# returns 1 with prob p, 0 otherwise
def bernoulli(p, rand):
    return (rand.random() <= p) * 1


# returns 0 with prob p, 1 otherwise
def one_minus_bernoulli(p, rand):
    return (rand.random() > p) * 1


def normalize_to_zero_one(m):
    minVal = np.amin(m)
    maxVal = float(np.amax(m))
    return m if maxVal <= minVal else (m - minVal) / (maxVal - minVal)


# Generators
seed = args.seed
if seed is None:
    import time

    seed = int(time.time() * 256) % (2**32)  # use fractional seconds

duelSelectionRandom = random.Random(seed)
reputationNoiseRandom = random.Random(seed + 1)
initialStateRandom = random.Random(seed + 2)

# Set seed also for numpy's random, which is used by scipy.stats as well
np.random.seed(seed + 3)

# Info about initial state,
# will be lazily initialized
occurringStrategiesNames = {}
occurringStrategies = set([])

occurringMorals = set([])
occurringInterestingMorals = set([])

# special player constants
HEAVEN = (-1, -1)
HELL = (-666, -666)
