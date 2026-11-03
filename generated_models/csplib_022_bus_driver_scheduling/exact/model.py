# csplib_022_bus_driver_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from exact import Exact


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    num_work = instance["num_work"]      # the number of pieces of work to cover
    num_shifts = instance["num_shifts"]  # the number of candidate shifts
    shifts = instance["shifts"]          # shifts[i]: the pieces of work that shift i covers

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is 1 when shift i is chosen, and 0 when not
    x = [f"x_{i}" for i in range(num_shifts)]
    for name in x:
        solver.addVariable(name, 0, 1)

    # Each piece of work is covered by exactly one chosen shift.
    for work in range(num_work):
        covering = [(1, x[i]) for i in range(num_shifts) if work in shifts[i]]
        solver.addConstraint(covering, True, 1, True, 1)

    # Every shift costs the same, so use as few shifts as possible.
    solver.setObjective([(1, name) for name in x], minimize=True)

    return solver, {"x": x}


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
