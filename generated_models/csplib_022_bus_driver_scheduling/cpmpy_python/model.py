# csplib_022_bus_driver_scheduling: a CPMpy model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

import cpmpy as cp


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    num_work = instance["num_work"]  # the number of pieces of work to cover
    shifts = instance["shifts"]      # shifts[i]: the pieces of work that shift i covers

    # x[i] is true when shift i is chosen
    x = cp.boolvar(shape=len(shifts), name="x")

    model = cp.Model()
    # Each piece of work is covered by exactly one chosen shift.
    for work in range(num_work):
        covering = [x[i] for i in range(len(shifts)) if work in shifts[i]]
        model.add(cp.sum(covering) == 1)

    # Choose as few shifts as possible.
    model.minimize(cp.sum(x))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
