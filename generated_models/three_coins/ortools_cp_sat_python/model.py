# three_coins: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install ortools`):
#   python three_coins.py three_coins.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Three coins lie on a table, in the order tails, heads, tails. In exactly
    the given number of moves, each move flipping one coin, make them all face
    either all heads or all tails."""
    initial = instance["init"]       # initial[j]: whether coin j starts tails up
    n_moves = instance["num_moves"]  # the number of moves
    n_coins = len(initial)           # the number of coins: 3

    model = cp_model.CpModel()

    # steps[m][j] is true when coin j is tails up after m moves
    steps = [[model.new_bool_var(f"s_{m}_{j}") for j in range(n_coins)] for m in range(n_moves + 1)]

    # The coins start as given.
    for j in range(n_coins):
        model.add(steps[0][j] == initial[j])

    for m in range(1, n_moves + 1):
        # flips[j] is true when move m flips coin j
        flips = []
        for j in range(n_coins):
            flip = model.new_bool_var(f"flip_{m}_{j}")
            # A flipped coin changes side, the others keep theirs.
            model.add(steps[m][j] != steps[m - 1][j]).only_enforce_if(flip)
            model.add(steps[m][j] == steps[m - 1][j]).only_enforce_if(~flip)
            flips.append(flip)
        # Each move flips exactly one coin.
        model.add(sum(flips) == 1)

    # After the last move the coins all face the same way.
    # all_tails is true when they all face tails up, and false when they all face heads up.
    all_tails = model.new_bool_var("all_tails")
    model.add(sum(steps[n_moves]) == n_coins).only_enforce_if(all_tails)
    model.add(sum(steps[n_moves]) == 0).only_enforce_if(~all_tails)

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
