# csplib_022_bus_driver_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

import z3


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    n_work = instance["num_work"]     # the number of pieces of work to cover
    n_shifts = instance["num_shifts"]  # the number of possible shifts
    shifts = instance["shifts"]        # shifts[i]: the pieces of work that shift i covers

    # x[i] is true when shift i is chosen
    x = [z3.Bool(f"x_{i}") for i in range(n_shifts)]

    solver = z3.Optimize()

    # Each piece of work is covered by exactly one chosen shift.
    for work in range(n_work):
        covering = [x[i] for i in range(n_shifts) if work in shifts[i]]
        if covering:
            solver.add(z3.PbEq([(s, 1) for s in covering], 1))
        else:
            # No shift covers this piece of work, so no schedule can cover it.
            solver.add(z3.BoolVal(False))

    # The number of chosen shifts.
    n_chosen = z3.Sum([z3.If(s, 1, 0) for s in x])

    solver.minimize(n_chosen)

    return solver, {"x": x}


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
