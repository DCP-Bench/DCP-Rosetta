# mario: a Python-MIP (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python mario.py mario.json

import mip


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's
    house and ends at Luigi's house, driving between houses on limited fuel."""
    n_houses = instance["nHouses"]        # the number of houses
    mario = instance["marioHouse"]        # the house where Mario starts
    luigi = instance["luigiHouse"]        # the house where the route ends
    arc_fuel = instance["arc_fuel"]       # arc_fuel[i][j]: the fuel to drive from house i to house j
    gold = instance["goldInHouse"]        # gold[i]: the gold in house i
    fuel_limit = instance["fuelLimit"]    # the most fuel the route may use

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[i][j] is 1 when the route drives directly from house i to house j, and 0 when not
    x = [[None] * n_houses for _ in range(n_houses)]
    for i in range(n_houses):
        for j in range(n_houses):
            if i != j:
                x[i][j] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)
    # v[i] is 1 when house i is on the route, and 0 when not
    v = [model.add_var(f"v_{i}", var_type=mip.BINARY) for i in range(n_houses)]
    # u[i] is the position of house i along the route, with Mario's house at 0
    u = [model.add_var(f"u_{i}", lb=0, ub=n_houses - 1, var_type=mip.INTEGER) for i in range(n_houses)]
    # s[i] is the house after house i on the route
    s = [model.add_var(f"s_{i}", lb=0, ub=n_houses - 1, var_type=mip.INTEGER) for i in range(n_houses)]

    # The route starts at Mario's house and ends at Luigi's house.
    model += v[mario] == 1
    model += v[luigi] == 1
    model += u[mario] == 0

    # The route drives from Luigi's house back to Mario's house.
    model += x[luigi][mario] == 1

    # A house on the route has one house after it and one before it. A house off the route has neither.
    for i in range(n_houses):
        model += mip.xsum(x[i][j] for j in range(n_houses) if j != i) == v[i]
        model += mip.xsum(x[j][i] for j in range(n_houses) if j != i) == v[i]

    # Positions go up by one along each drive, except the drive back to Mario's house. So the
    # route is one path from Mario's house, with no separate loop among the other houses. A drive
    # that is not made is released by n_houses.
    for i in range(n_houses):
        for j in range(n_houses):
            if i != j and j != mario:
                model += u[j] >= u[i] + 1 - n_houses * (1 - x[i][j])

    # The fuel used by the drives on the route stays within the limit.
    model += mip.xsum(arc_fuel[i][j] * x[i][j] for i in range(n_houses) for j in range(n_houses) if i != j) <= fuel_limit

    # The house after house i is the house the route drives to from it. A house off the route is its own successor.
    for i in range(n_houses):
        model += s[i] == mip.xsum(j * x[i][j] for j in range(n_houses) if j != i) + i - i * v[i]

    # The gold collected is the total gold of the houses on the route.
    model.objective = mip.xsum(gold[i] * v[i] for i in range(n_houses))

    return model, {"s": s}


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
