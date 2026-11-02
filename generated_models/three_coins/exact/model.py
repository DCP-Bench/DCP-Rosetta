# three_coins: an Exact (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python three_coins.py three_coins.json

from exact import Exact


def create_model(instance):
    """Three coins lie on a table, each heads or tails. In exactly the given number of
    moves, each move turning over one coin, make them all face heads or all face tails."""
    num_moves = instance["num_moves"]  # the number of moves, each turning over one coin
    init = instance["init"]            # init[j]: 1 when coin j starts tails up, 0 when heads up
    n_coins = len(init)                # the number of coins

    solver = Exact()

    # steps[m][j] is 1 when coin j is tails up after m moves, and 0 when heads up
    steps = [[f"steps_{m}_{j}" for j in range(n_coins)] for m in range(num_moves + 1)]

    # Exact identifies its variables by name.
    # The first row is the starting position of the coins.
    for j in range(n_coins):
        solver.addVariable(steps[0][j], init[j], init[j])
    for row in steps[1:]:
        for name in row:
            solver.addVariable(name, 0, 1)

    for m in range(1, num_moves + 1):
        # flipped[j] is 1 when move m turns coin j over
        flipped = [f"flipped_{m}_{j}" for j in range(n_coins)]
        for j in range(n_coins):
            before, after, flip = steps[m - 1][j], steps[m][j], flipped[j]
            solver.addVariable(flip, 0, 1)
            # A coin is turned over exactly when its face changes.
            solver.addConstraint([(1, flip), (-1, before), (-1, after)], False, 0, True, 0)
            solver.addConstraint([(1, flip), (1, before), (1, after)], False, 0, True, 2)
            solver.addConstraint([(1, flip), (-1, before), (1, after)], True, 0)
            solver.addConstraint([(1, flip), (1, before), (-1, after)], True, 0)
        # Each move turns over exactly one coin.
        solver.addConstraint([(1, flip) for flip in flipped], True, 1, True, 1)

    # all_tails is 1 when the coins end all tails up, and 0 when they end all heads up.
    solver.addVariable("all_tails", 0, 1)
    # The last row is all tails or all heads.
    solver.addConstraint([(1, name) for name in steps[num_moves]] + [(-n_coins, "all_tails")],
                         True, 0, True, 0)

    return solver, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
