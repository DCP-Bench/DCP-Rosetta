# aircraft_assignment: a hermax (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install hermax`):
#   python aircraft_assignment.py aircraft_assignment.json

from hermax.model import Model


def create_model(instance):
    """Assign aircraft of several types to several routes so that every route's passenger
    demand is met, no aircraft type is used beyond its available units, and the total
    operational cost is as small as possible."""
    availability = instance["availability"]  # availability[i]: units available of aircraft type i
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: operational cost of one aircraft of type i on route j
    demand = instance["demand"]              # demand[j]: passengers that must be carried on route j
    num_types = len(availability)            # number of aircraft types
    num_routes = len(demand)                 # number of routes

    m = Model()

    # allocation[i][j] is the number of aircraft of type i assigned to route j,
    # between 0 and the number of units of type i
    allocation = [[m.int(f"allocation_{i}_{j}", 0, availability[i])
                   for j in range(num_routes)]
                  for i in range(num_types)]

    # Every route's demand is met: the seats of all aircraft assigned to it cover its demand.
    for j in range(num_routes):
        m &= (sum(capabilities[i][j] * allocation[i][j] for i in range(num_types)) >= demand[j])

    # No aircraft type is over-assigned: the aircraft of each type used over all routes
    # stay within its available units.
    for i in range(num_types):
        m &= (sum(allocation[i][j] for j in range(num_routes)) <= availability[i])

    # Minimise the total operational cost of all assigned aircraft.
    m.obj += sum(costs[i][j] * allocation[i][j]
                 for i in range(num_types) for j in range(num_routes))

    return m, {"allocation": allocation}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
