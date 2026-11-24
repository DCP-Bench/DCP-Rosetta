# aircraft_assignment: a SCIP (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python aircraft_assignment.py aircraft_assignment.json
import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Aircraft assignment: each aircraft type has a limited number of units
    and each route has a passenger demand. Decide how many aircraft of each
    type fly each route so that every route carries its demand, no type is
    flown more often than it is available, and the total operational cost
    is as small as possible."""
    availability = np.array(instance["availability"])  # availability[i]: the number of aircraft of type i that exist
    demand = np.array(instance["demand"])              # demand[j]: the passengers route j must carry
    capabilities = np.array(instance["capabilities"])  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = np.array(instance["costs"])                # costs[i][j]: operational cost of one aircraft of type i flying route j

    # The number of aircraft types and the number of routes.
    n_types = len(availability)
    n_routes = len(demand)

    model = Model("aircraft_assignment")

    # allocation[i, j] is the number of aircraft of type i assigned to route j.
    # Its upper bound is the number of aircraft of type i, since no more can fly
    # (the bound comes from the availability field of the instance).
    allocation = model.addMatrixVar(
        (n_types, n_routes), vtype="I", lb=0,
        ub=np.broadcast_to(availability[:, None], (n_types, n_routes)),
    )

    # Each aircraft type has a limited number of units: the aircraft of type i
    # assigned to all routes add up to no more than availability[i].
    model.addMatrixCons(allocation.sum(axis=1) <= availability)

    # Every route's passenger demand must be met: the seats of all aircraft
    # assigned to the route, capabilities[i, j] per aircraft, cover demand[j].
    model.addMatrixCons((capabilities * allocation).sum(axis=0) >= demand)

    # Minimise the total operational cost of all aircraft assigned to all routes.
    model.setObjective((costs * allocation).sum(), "minimize")

    return model, {"allocation": allocation}


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
