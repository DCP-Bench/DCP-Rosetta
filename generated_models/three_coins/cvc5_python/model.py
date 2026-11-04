# three_coins: a cvc5 (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python three_coins.py three_coins.json

import cvc5.pythonic as c5


def create_model(instance):
    """Three coins lie on a table. In exactly the given number of moves, each flipping
    one coin, make them all face heads or all face tails."""
    init = instance["init"]            # init[c]: 1 when coin c starts tails up, 0 when it starts heads up
    num_moves = instance["num_moves"]  # the number of moves, each flipping one coin
    n_coins = len(init)                # the number of coins: 3

    # steps[t][c] is true when coin c is tails up after t moves (t = 0 is the start)
    steps = [[c5.Bool(f"steps_{t}_{c}") for c in range(n_coins)] for t in range(num_moves + 1)]

    solver = c5.Solver()

    # The coins start as given.
    solver.add([steps[0][c] if init[c] == 1 else c5.Not(steps[0][c]) for c in range(n_coins)])

    # Each move flips exactly one coin.
    for t in range(num_moves):
        flips = [c5.If(c5.Not(steps[t][c] == steps[t + 1][c]), 1, 0) for c in range(n_coins)]
        solver.add(c5.Sum(flips) == 1)

    # After the last move all coins face the same way.
    last = steps[num_moves]
    solver.add(c5.Or(c5.And(last), c5.And([c5.Not(b) for b in last])))

    return solver, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
