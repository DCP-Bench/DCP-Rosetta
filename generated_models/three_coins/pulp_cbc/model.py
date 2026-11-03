# three_coins: a PuLP (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python three_coins.py three_coins.json

import pulp


def create_model(instance):
    """Three coins lie on a table. In exactly the given number of moves, each move
    turning over one coin, make them all face the same way: all heads or all tails."""
    init = instance["init"]            # init[j]: whether coin j starts tails up
    num_moves = instance["num_moves"]  # the number of moves
    n_coins = len(init)

    problem = pulp.LpProblem("three_coins", pulp.LpMinimize)

    # steps[m][j] is true when coin j is tails up after m moves; row 0 is the start.
    # The start row is fixed to the given sides.
    steps = [[pulp.LpVariable(f"s_0_{j}", cat="Integer", lowBound=init[j], upBound=init[j])
              for j in range(n_coins)]]
    steps += [[pulp.LpVariable(f"s_{m}_{j}", cat="Binary") for j in range(n_coins)]
              for m in range(1, num_moves + 1)]

    for m in range(1, num_moves + 1):
        # flip[j] is true when move m turns coin j over.
        flips = []
        for j in range(n_coins):
            before, after = steps[m - 1][j], steps[m][j]
            flip = pulp.LpVariable(f"flip_{m}_{j}", cat="Binary")
            # A coin is turned over exactly when its side changes between the two rows.
            problem += flip >= before - after
            problem += flip >= after - before
            problem += flip <= before + after
            problem += flip <= 2 - before - after
            flips.append(flip)
        # Each move turns over exactly one coin.
        problem += pulp.lpSum(flips) == 1

    # all_tails is true when the coins end all tails up, and false when they end all heads up.
    all_tails = pulp.LpVariable("all_tails", cat="Binary")
    # After the last move the coins all face the same way.
    problem += pulp.lpSum(steps[num_moves]) == n_coins * all_tails

    return problem, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
