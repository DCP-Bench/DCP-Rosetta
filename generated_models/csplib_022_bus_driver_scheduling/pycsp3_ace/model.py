# csplib_022_bus_driver_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Bus driver scheduling: a set of tasks (pieces of work) must be covered, and a
    large set of possible shifts is given, each covering a subset of the tasks. Select
    a subset of shifts that covers each piece of work exactly once, using as few
    shifts as possible. The cost of each shift is the same."""
    n_work = instance["num_work"]  # the pieces of work, numbered from 0
    shifts = instance["shifts"]  # shifts[s] lists the pieces of work that shift s covers
    n_shifts = len(shifts)

    # x[s] is 1 when shift s is selected and 0 when it is not
    x = VarArray(size=n_shifts, dom={0, 1})

    satisfy(
        # each piece of work w is covered by exactly one selected shift
        Sum(x[s] for s in range(n_shifts) if w in shifts[s]) == 1 for w in range(n_work)
    )

    # the number of selected shifts, which is to be minimised (every shift costs 1)
    minimize(Sum(x))

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
