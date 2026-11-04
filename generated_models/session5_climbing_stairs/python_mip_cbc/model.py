# session5_climbing_stairs: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import mip


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, where a move takes 0 steps once
    the top of the stair is reached."""
    n_steps = instance["n"]  # the number of steps in the stair
    m1 = instance["m1"]      # the fewest steps taken in one move
    m2 = instance["m2"]      # the most steps taken in one move

    model = mip.Model(solver_name="CBC")

    # steps[i] is the number of steps taken at move i.
    steps = [model.add_var(f"steps_{i}", lb=0, ub=m2, var_type=mip.INTEGER) for i in range(n_steps)]
    # moved[i] is 1 when move i is made, and 0 once the top has been reached.
    moved = [model.add_var(f"moved_{i}", var_type=mip.BINARY) for i in range(n_steps)]

    # A move that is made takes between m1 and m2 steps, and a move that is not made takes none.
    for i in range(n_steps):
        model.add_constr(steps[i] >= m1 * moved[i])
        model.add_constr(steps[i] <= m2 * moved[i])

    # Once a move is not made, no later move is made.
    for i in range(n_steps - 1):
        model.add_constr(moved[i] >= moved[i + 1])

    # The moves add up to the whole stair.
    model.add_constr(mip.xsum(steps) == n_steps)

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
