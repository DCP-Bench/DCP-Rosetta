# csplib_022_bus_driver_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

import pulp


def create_model(instance):
    """Cover every piece of work with exactly one shift, chosen from a given set of
    possible shifts that each cover some of the pieces of work. Every shift costs
    the same, so use as few shifts as possible."""
    n_work = instance["num_work"]        # the number of pieces of work to cover
    n_shifts = instance["num_shifts"]    # the number of possible shifts
    shifts = instance["shifts"]          # shifts[i]: the pieces of work that shift i covers

    problem = pulp.LpProblem("bus_driver_scheduling", pulp.LpMinimize)

    # x[i] is 1 when shift i is chosen, and 0 when not
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(n_shifts)]

    # Each piece of work is covered by exactly one chosen shift.
    for work in range(n_work):
        problem += pulp.lpSum(x[i] for i in range(n_shifts) if work in shifts[i]) == 1

    # Use as few shifts as possible.
    problem += pulp.lpSum(x)

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
