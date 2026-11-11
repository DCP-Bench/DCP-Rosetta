# aircraft_assignment: a PyCSP3 model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python aircraft_assignment.py aircraft_assignment.json

from pycsp3 import *


def create_model(instance):
    """Assign several types of aircraft to a set of routes so that every route's passenger
    demand is met, each aircraft type is used no more than its availability, and the total
    operational cost is as small as possible."""
    availability = instance["availability"]  # availability[i]: how many aircraft of type i there are
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: operational cost of one aircraft of type i on route j
    demand = instance["demand"]              # demand[j]: passengers that must be carried on route j
    n_types = len(availability)
    n_routes = len(demand)

    # allocation[i][j] is the number of aircraft of type i assigned to route j. No type can
    # be assigned more aircraft than it has, so the largest count is the largest availability.
    max_units = max(availability)
    allocation = VarArray(size=[n_types, n_routes], dom=range(max_units + 1))

    satisfy(
        # Each type of aircraft is assigned to the routes at most as often as it is available.
        [Sum(allocation[i]) <= availability[i] for i in range(n_types)],
        # The passengers carried on each route, by all aircraft types together, meet its demand.
        [Sum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= demand[j] for j in range(n_routes)],
    )

    # Minimise the total operational cost of all the aircraft assigned to the routes.
    minimize(Sum(costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)))

    return {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("allocation", "=")
        for row in outputs["allocation"]:
            print(values(row))
    else:
        print("No solution:", status())
