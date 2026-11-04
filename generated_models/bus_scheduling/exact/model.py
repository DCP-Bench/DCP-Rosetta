# bus_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python bus_scheduling.py bus_scheduling.json

from exact import Exact


def create_model(instance):
    """The day is cut into equal time slots, and each bus works two successive slots. Choose how
    many buses start in each slot so that every slot's demand is met, with as few buses as
    possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    n_slots = len(demands)         # the number of time slots in the day

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is the number of buses that start working in slot i
    x = [f"x_{i}" for i in range(n_slots)]
    for name in x:
        solver.addVariable(name, 0, sum(demands))

    # The buses on duty in a slot are those that started in it and those that started in the
    # slot before. The day wraps around, so the first slot follows the last.
    for s in range(n_slots):
        before = (s - 1) % n_slots
        solver.addConstraint([(1, x[before]), (1, x[s])], True, demands[s])

    # Use as few buses as possible.
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
