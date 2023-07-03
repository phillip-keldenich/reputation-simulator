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
