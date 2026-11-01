# aircraft_assignment: a CPMpy model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python aircraft_assignment.py aircraft_assignment.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = np.array(instance["availability"])    # availability[i]: aircraft available of type i
    demand = np.array(instance["demand"])                # demand[j]: passengers to carry on route j
    capabilities = np.array(instance["capabilities"])    # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = np.array(instance["costs"])                  # costs[i][j]: cost of one aircraft of type i on route j
    n_types, n_routes = capabilities.shape

    # allocation[i, j] is the number of aircraft of type i assigned to route j.
    # No type is ever needed more than its whole fleet on one route, so the
    # largest fleet bounds every entry.
    allocation = cp.intvar(0, int(availability.max()), shape=(n_types, n_routes), name="allocation")

    model = cp.Model()
    # A type is not assigned more aircraft than are available.
    model.add(allocation.sum(axis=1) <= availability)
    # The aircraft on each route together carry at least the route's demand.
    model.add((allocation * capabilities).sum(axis=0) >= demand)
    # Minimise the total operating cost.
    model.minimize(cp.sum(allocation * costs))

    return model, {"allocation": allocation}


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
