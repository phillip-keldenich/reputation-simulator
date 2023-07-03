# Copyright 2023 
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

# support for python 3
try:
    xrange
except NameError:
    xrange = range


def setup_diagonal(strategy):
    from misc_globals import strategies, N

    for x in xrange(N):
        strategies[x, x] = strategy


def setup_cluster(center_strategy):
    from misc_globals import N

    setup_cluster_at(center_strategy, N / 2, N / 2)


def setup_cluster_at(center_strategy, middle_x, middle_y):
    from misc_globals import strategies

    # Cluster size from command line
    from cmdline_args import args

    s = args.s
    strategies[
        int(middle_x - s / 2) : int(middle_x + s / 2 + s % 2),
        int(middle_y - s / 2) : int(middle_y + s / 2 + s % 2),
    ] = center_strategy


def setup_circle(center_strategy):
    from misc_globals import strategies, N

    # Radius s from command line
    from cmdline_args import args

    s = args.s
    for x in xrange(N):
        for y in xrange(N):
            if (x - N / 2.0) ** 2 + (y - N / 2.0) ** 2 < s**2:
                strategies[x, y] = center_strategy


def horizontal_split_strategies(upper_strategy, lower_strategy):
    from misc_globals import strategies, N

    strategies[: int(N / 2), :] = upper_strategy
    strategies[int(N / 2) :, :] = lower_strategy


def vertical_split_strategies(left_strategy, right_strategy):
    from misc_globals import strategies, N

    strategies[:, : int(N / 2)] = left_strategy
    strategies[:, int(N / 2) :] = right_strategy


def diagonal_split_strategies(upper_strategy, lower_strategy):
    from misc_globals import strategies, N

    strategies[:] = upper_strategy
    for x in xrange(N):
        for y in xrange(x):
            strategies[x, y] = lower_strategy


def chess_board_strategies(strategy1, strategy2, field_size):
    from misc_globals import strategies, N

    top_row = 0
    parity = False
    bottom_row = top_row + field_size
    while bottom_row <= N:
        left_col = 0
        right_col = field_size
        cur_strat = strategy2 if parity else strategy1
        off_strat = strategy1 if parity else strategy2
        while right_col <= N:
            strategies[top_row:bottom_row, left_col:right_col] = cur_strat
            left_col = right_col
            right_col += field_size
            cur_strat, off_strat = off_strat, cur_strat
        strategies[top_row:bottom_row, left_col:] = cur_strat
        top_row = bottom_row
        bottom_row += field_size
        parity = not parity
    left_col = 0
    right_col = field_size
    cur_strat = strategy2 if parity else strategy1
    off_strat = strategy1 if parity else strategy2
    while right_col <= N:
        strategies[top_row:, left_col:right_col] = cur_strat
        left_col = right_col
        right_col += field_size
        cur_strat, off_strat = off_strat, cur_strat
    strategies[top_row:, left_col:] = cur_strat


def probabilistic_diagonal_split(upper_strategy, lower_strategy):
    from cmdline_args import args
    from misc_globals import initialStateRandom, bernoulli, strategies, N

    prob = args.prob_for_init
    drawStrategiesIid([lower_strategy, upper_strategy], [prob, 1 - prob])
    for x in xrange(N):
        for y in xrange(x):
            strategies[x, y] = (
                upper_strategy
                if bernoulli(args.prob_for_init, initialStateRandom) == 1
                else lower_strategy
            )


def cluster_strategy(fill_strategy, center_strategy):
    from misc_globals import strategies

    # First, set all players strategy to fill_strategy
    strategies[:] = fill_strategy
    # then, overwrite s x s cluster in middle by center_strategy
    setup_cluster(center_strategy)


def two_clusters_strategy(fill_strategy, cluster_strategy1, cluster_strategy2):
    from misc_globals import strategies, N

    # First, set all players strategy to fill_strategy
    strategies[:] = fill_strategy
    # then, overwrite s x s cluster in middle by center_strategy
    setup_cluster_at(cluster_strategy1, N / 4, N / 4)
    setup_cluster_at(cluster_strategy2, 3 * N / 4, 3 * N / 4)


def circle_strategy(fill_strategy, center_strategy):
    from misc_globals import strategies

    # First, set all players strategy to fill_strategy
    strategies[:] = fill_strategy
    # then, create discrete circle with radius s
    setup_circle(center_strategy)


def drawStrategiesIid(strategiesToUse, strategyProbs):
    from misc_globals import strategies, N
    from scipy import stats

    strategiesDistribution = stats.rv_discrete(
        values=(strategiesToUse, strategyProbs), name="strategies-dist"
    )
    strategies[:] = strategiesDistribution.rvs(size=(N, N))


def random_strategy_clusters(strategiesToUse, strategyProbs):
    from misc_globals import initialStateRandom, strategies, N
    from scipy import stats
    from cmdline_args import args

    strategiesDistribution = stats.rv_discrete(
        values=(strategiesToUse, strategyProbs), name="strategies-dist"
    )
    s = args.s
    strategies[:] = strategiesToUse[0]
    for _ in xrange(10 * (int(N / s)) ** 2):
        strategy = strategiesDistribution.rvs()
        rx = initialStateRandom.uniform(0, N)
        ry = initialStateRandom.uniform(0, N)
        for x in xrange(N):
            for y in xrange(N):
                if (x - rx) ** 2 + (y - ry) ** 2 < s**2:
                    strategies[x, y] = strategy


def few_random_strategy_clusters(
    fillStrategy, nClusters, clusterStrategies, clusterStrategyProbs
):
    from misc_globals import initialStateRandom, strategies, N
    from scipy import stats
    from cmdline_args import args

    strategiesDistribution = stats.rv_discrete(
        values=(clusterStrategies, clusterStrategyProbs), name="strategies-dist"
    )
    s = args.s
    strategies[:] = fillStrategy
    for _ in xrange(nClusters):
        strategy = strategiesDistribution.rvs()
        rx = initialStateRandom.uniform(0, N)
        ry = initialStateRandom.uniform(0, N)
        for x in xrange(N):
            for y in xrange(N):
                if (x - rx) ** 2 + (y - ry) ** 2 < s**2:
                    strategies[x, y] = strategy


def random_strategies(strategy1, strategy2):
    from cmdline_args import args

    prob = args.prob_for_init
    drawStrategiesIid([strategy1, strategy2], [prob, 1 - prob])


def two_clusters(strategy1, strategy2, distance):
    from misc_globals import strategies, N

    # Cluster size from command line
    from cmdline_args import args

    s = args.s
    strategies[
        int(N / 2 - s / 2) : int(N / 2 + s / 2 + s % 2),
        int(N / 2 - s / 2 - distance) : int(N / 2 + s / 2 + s % 2 - distance),
    ] = strategy1
    strategies[
        int(N / 2 - s / 2) : int(N / 2 + s / 2 + s % 2),
        int(N / 2 - s / 2 + distance) : int(N / 2 + s / 2 + s % 2 + distance),
    ] = strategy2


def custom_strategies():
    from cmdline_args import args

    if args.initial_strategies_script is None:
        print(
            'You specified "custom" initial strategies, but did not give me a script!'
        )
        exit(42)
    else:
        exec(args.initial_strategies_script)


import strategies
from strategies import (
    allDefect,
    allCooperate,
    saferep,
    mafia,
    mafia2,
    kandori1,
    kandori2,
    kandori3,
    kandori8,
    kandori9,
    democrats,
    kandoriInitiallyGood,
    democrats2,
    republicans2,
    safedirep,
    safedirep2,
)

# To define new scenarios, simply add them to the list and add a callable
# object as value that does the initialization. Command line arguments a.s.o. are
# automatically derived from this.
scenarios = {
    # The cluster scenarios are added automatically for all pairs of strategies
    # 'allD_ClusterSaferep':  (lambda: cluster_strategy(allDefect,    saferep)),
    # 'allD_ClusterAllC':     (lambda: cluster_strategy(allDefect,    allCooperate)),
    # 'allC_ClusterAllD':     (lambda: cluster_strategy(allCooperate, allDefect)),
    # 'allC_ClusterSaferep':  (lambda: cluster_strategy(allCooperate, saferep)),
    # 'allD_ClusterMafia':    (lambda: cluster_strategy(allDefect,    mafia)),
    # 'allC_ClusterMafia':    (lambda: cluster_strategy(allCooperate, mafia)),
    # 'allD_ClusterKandori1': (lambda: cluster_strategy(allDefect,    kandori1)),
    # 'allC_ClusterKandori1': (lambda: cluster_strategy(allCooperate, kandori1)),
    # 'allD_ClusterKandori2': (lambda: cluster_strategy(allDefect,    kandori2)),
    # 'allC_ClusterKandori2': (lambda: cluster_strategy(allCooperate, kandori2)),
    # 'allD_ClusterKandori3': (lambda: cluster_strategy(allDefect,    kandori3)),
    # 'allC_ClusterKandori3': (lambda: cluster_strategy(allCooperate, kandori3)),
    # 'allD_ClusterKandori8': (lambda: cluster_strategy(allDefect,    kandori8)),
    # 'allC_ClusterKandori8': (lambda: cluster_strategy(allCooperate, kandori8)),
    # 'allD_ClusterKandori9': (lambda: cluster_strategy(allDefect,    kandori9)),
    # 'allC_ClusterKandori9': (lambda: cluster_strategy(allCooperate, kandori9)),
    "allD_CircleMafia": (lambda: circle_strategy(allDefect, mafia)),
    "allC_CircleMafia": (lambda: circle_strategy(allCooperate, mafia)),
    "halfAllD_half_AllC_ClusterSaferep": (
        lambda: (
            vertical_split_strategies(allCooperate, allDefect),
            setup_cluster(saferep),
        )
    ),
    "halfAllD_halfAllC_ClusterMafia": (
        lambda: (
            vertical_split_strategies(allCooperate, allDefect),
            setup_cluster(mafia),
        )
    ),
    "halfMafia_halfSaferep": (lambda: vertical_split_strategies(mafia, saferep)),
    "DemRep": (lambda: horizontal_split_strategies(democrats, saferep)),
    "DemDem": (lambda: horizontal_split_strategies(democrats, democrats2)),
    "DemRepRandomInit": (lambda: random_strategies(saferep, democrats)),
    "DemRepDiagonal": (
        lambda: (
            diagonal_split_strategies(democrats, saferep),
            setup_diagonal(allCooperate),
        )
    ),
    "DemRepRandomDiagonal": (lambda: probabilistic_diagonal_split(democrats, saferep)),
    "DemRepAllDAllCRandom": (
        lambda: drawStrategiesIid(
            [democrats, saferep, allDefect, allCooperate], [0.25, 0.25, 0.25, 0.25]
        )
    ),
    "DemDemRandomInit": (lambda: random_strategies(democrats, democrats2)),
    "MafiaMafia2RandomInit": (lambda: random_strategies(mafia, mafia2)),
    "MafiaSaferepRandomInit": (lambda: random_strategies(saferep, mafia)),
    "dem_ClusterRep": (lambda: cluster_strategy(democrats, saferep)),
    "kandoriDemRep": (lambda: random_strategies(kandoriInitiallyGood, kandori8)),
    "AllDAllC_ClusterDemRep": (
        lambda: (
            vertical_split_strategies(allCooperate, allDefect),
            two_clusters(saferep, democrats, 20),
        )
    ),
    "DemDemDiagonal": (
        lambda: (
            diagonal_split_strategies(democrats, democrats2),
            setup_diagonal(allCooperate),
        )
    ),
    "RepRepDiagonal": (
        lambda: (
            diagonal_split_strategies(saferep, republicans2),
            setup_diagonal(allCooperate),
        )
    ),
    "DemSafedirep": (lambda: (random_strategies(safedirep, safedirep2))),
    "SafedirepSaferep": (lambda: horizontal_split_strategies(saferep, safedirep)),
    "SafedirepSaferepRandomInit": (lambda: random_strategies(saferep, safedirep)),
    "SafedirepSafedirep2Chessboard": (
        lambda: chess_board_strategies(safedirep, safedirep2, 20)
    ),
    "LiberalLiberal2": (lambda: horizontal_split_strategies(democrats, democrats2)),
    "SafedirepSafedirep2": (lambda: horizontal_split_strategies(safedirep, safedirep2)),
    "SafedirepSafedirep2WithAllDAllC": (
        lambda: drawStrategiesIid(
            [safedirep, safedirep2, allDefect, allCooperate], [0.45, 0.45, 0.05, 0.05]
        )
    ),
    "SafedirepSafedirep2WithAllDAllCClusters": (
        lambda: random_strategy_clusters(
            [safedirep, safedirep2, allDefect, allCooperate], [0.4, 0.4, 0.1, 0.1]
        )
    ),
    "SafedirepSaferepRandomClusters": (
        lambda: random_strategy_clusters([safedirep, saferep], [0.5, 0.5])
    ),
    "SafedirepSaferepFewRandomClusters": (
        lambda: few_random_strategy_clusters(safedirep, 5, [saferep], [1.0])
    ),
    "SafedirepSafedirep2RandomInit": (lambda: random_strategies(safedirep, safedirep2)),
    "SafedirepClusterSaferep": (lambda: cluster_strategy(safedirep, democrats)),
    "allD_ClusterDemRep": (
        lambda: few_random_strategy_clusters(
            allDefect, 30, [democrats2, democrats], [0.5, 0.5]
        )
    ),
    "AllRandom": (
        lambda: drawStrategiesIid(
            list(strategies.strategyName.keys()),
            strategies.numberOfDifferentStrategies
            * [1.0 / strategies.numberOfDifferentStrategies],
        )
    ),
    "custom": (lambda: custom_strategies()),
}

# add cluster scenarios for all pairs
for strategy1 in strategies.scenarioStrategyNames:
    name1 = strategies.strategyName[strategy1]
    for strategy2 in strategies.scenarioStrategyNames:
        if strategy1 != strategy2:
            name2 = strategies.strategyName[strategy2]
            name2 = name2[0].upper() + name2[1:]
            scenarioName = "{}_Cluster{}".format(name1, name2)
            scenarios[
                scenarioName
            ] = lambda strat1=strategy1, strat2=strategy2: cluster_strategy(
                strat1, strat2
            )
