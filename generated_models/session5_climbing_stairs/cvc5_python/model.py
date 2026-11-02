# session5_climbing_stairs: a cvc5 (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import cvc5.pythonic as c5


def create_model(instance):
    """Climb a stair of n steps, taking between the fewest and the most steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n_steps = instance["n"]   # the number of steps in the stair
    least = instance["m1"]    # the fewest steps taken at a move
    most = instance["m2"]     # the most steps taken at a move

    # steps[i] is the number of steps taken at move i, 0 once the top is reached
    steps = [c5.Int(f"steps_{i}") for i in range(n_steps)]

    solver = c5.Solver()

    # A move takes between the fewest and the most steps, or none at all.
    solver.add([c5.Or(s == 0, c5.And(s >= least, s <= most)) for s in steps])
    # Once a move takes no steps, every later move takes none too.
    solver.add([c5.Implies(steps[i] == 0, steps[i + 1] == 0) for i in range(n_steps - 1)])
    # The moves add up to the whole stair.
    solver.add(c5.Sum(steps) == n_steps)

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
