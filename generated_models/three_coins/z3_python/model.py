# three_coins: a Z3 (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python three_coins.py three_coins.json

import z3


def create_model(instance):
    """Three coins lie on a table, in the order tails, heads, tails. In exactly
    the given number of moves, each move turning over one coin, make them all
    face either all heads or all tails."""
    initial = instance["init"]       # initial[j]: whether coin j starts tails up
    n_moves = instance["num_moves"]  # the number of moves
    n_coins = len(initial)           # the number of coins

    # steps[m][j] is true when coin j is tails up after m moves (step 0 is the start)
    steps = [[z3.Bool(f"s_{m}_{j}") for j in range(n_coins)] for m in range(n_moves + 1)]

    solver = z3.Solver()

    # The coins start as given.
    solver.add([steps[0][j] == bool(initial[j]) for j in range(n_coins)])

    # Each move turns over exactly one coin.
    for m in range(1, n_moves + 1):
        # turned[j] is 1 when coin j has changed side in move m
        turned = [z3.If(steps[m][j] != steps[m - 1][j], 1, 0) for j in range(n_coins)]
        solver.add(z3.Sum(turned) == 1)

    # tails_at_end counts the coins that are tails up after the last move
    tails_at_end = z3.Sum([z3.If(steps[n_moves][j], 1, 0) for j in range(n_coins)])

    # After the last move the coins all face the same way.
    solver.add(z3.Or(tails_at_end == 0, tails_at_end == n_coins))

    return solver, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
