# session5_climbing_stairs: a Z3 (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import z3


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n_steps = instance["n"]   # the number of steps in the stair
    least = instance["m1"]    # the fewest steps taken at a move
    most = instance["m2"]     # the most steps taken at a move

    # steps[i] is the number of steps taken at move i, 0 once the top is reached
    steps = [z3.Int(f"steps_{i}") for i in range(n_steps)]

    solver = z3.Solver()

    # A move takes no more than the most steps allowed, and none is negative.
    solver.add([z3.And(s >= 0, s <= most) for s in steps])
    # A move takes at least the fewest steps allowed, or none at all.
    solver.add([z3.Or(s >= least, s == 0) for s in steps])
    # The moves add up to the whole stair.
    solver.add(z3.Sum(steps) == n_steps)
    # Once a move takes no steps, every later move takes none too.
    solver.add([z3.Implies(steps[i - 1] == 0, steps[i] == 0) for i in range(1, n_steps)])

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
