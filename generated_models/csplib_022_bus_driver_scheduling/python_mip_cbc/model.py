# csplib_022_bus_driver_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

import mip


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    n_work = instance["num_work"]  # the number of pieces of work to cover
    shifts = instance["shifts"]    # shifts[j]: the pieces of work that shift j covers
    n_shifts = len(shifts)         # the number of possible shifts

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[j] is 1 when shift j is selected, and 0 when not
    x = [model.add_var(f"x_{j}", var_type=mip.BINARY) for j in range(n_shifts)]

    # covers[w] lists the shifts that cover piece of work w
    covers = [[] for _ in range(n_work)]
    for j, shift in enumerate(shifts):
        for w in shift:
            covers[w].append(j)

    # Each piece of work is covered by exactly one selected shift.
    for w in range(n_work):
        model.add_constr(mip.xsum(x[j] for j in covers[w]) == 1)

    # The cost is the number of shifts selected, since every shift costs the same.
    model.objective = mip.xsum(x)

    return model, {"x": x}


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
