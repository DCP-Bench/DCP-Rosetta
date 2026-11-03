# csplib_022_bus_driver_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Bus driver scheduling: choose the fewest shifts so that every piece of
    work is covered by exactly one chosen shift. Each shift covers a subset of
    the pieces of work, and every shift costs the same."""
    num_work = instance["num_work"]    # the pieces of work, numbered 0 to num_work - 1
    num_shifts = instance["num_shifts"]  # the candidate shifts, numbered 0 to num_shifts - 1
    shifts = instance["shifts"]        # shifts[j]: the list of pieces of work that shift j covers

    model = Model("csplib_022_bus_driver_scheduling")

    # x[j] is 1 when shift j is selected, and 0 when it is not
    x = [model.addVar(f"x_{j}", vtype="B") for j in range(num_shifts)]

    # Every piece of work is covered by exactly one selected shift: the selected
    # shifts that contain work w must add up to exactly 1.
    for w in range(num_work):
        model.addCons(quicksum(x[j] for j in range(num_shifts) if w in shifts[j]) == 1)

    # Use as few shifts as possible (each shift costs the same).
    model.setObjective(quicksum(x), "minimize")

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
