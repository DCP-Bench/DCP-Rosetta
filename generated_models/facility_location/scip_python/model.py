# facility_location: a SCIP (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python facility_location.py facility_location.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Facility location: choose which candidate warehouses to open, and how many units each
    open warehouse ships to each region, so that the opening costs plus the shipping costs are
    as small as possible. Every region gets exactly its demand, a warehouse ships at most its
    capacity, and a closed warehouse ships nothing."""
    names = instance["warehouse_s"]                       # names of the candidate cities, one per warehouse
    fixed_costs = np.array(instance["fixed_costs"])       # fixed_costs[i]: cost of opening warehouse i
    capacity = instance["max_shipping"]                   # most units one warehouse can ship in total
                                                          # (assumption: the statement does not give it, the field name does)
    demands = np.array(instance["demands"])               # demands[j]: units region j needs
    shipping_costs = np.array(instance["shipping_costs"]) # shipping_costs[i][j]: cost of one unit from warehouse i to region j

    # The restrictions name cities, so find their positions in the warehouse list.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    model = Model("facility_location")

    # open_warehouse[i] is 1 when warehouse i is opened, and 0 when it is not
    open_warehouse = model.addMatrixVar((len(names),), vtype="B", name="open_warehouse")

    # ships[i, j] is the number of units shipped from warehouse i to region j.
    # A warehouse ships at most its capacity in total (the capacity constraint below), so no cell
    # can exceed it; the upper bound here only gives each cell a finite bound.
    ships = model.addMatrixVar((len(names), len(demands)), vtype="I", lb=0, ub=capacity, name="ships")

    # total_cost is the total cost, the quantity to minimise. It is a bounded integer, so that the
    # optimum can be pinned when further optimal solutions are listed. Its upper bound is derived
    # from the data: opening every warehouse once, plus shipping all demand at the most expensive rate.
    total_cost = model.addVar("total_cost", vtype="I", lb=0,
                              ub=fixed_costs.sum() + demands.sum() * shipping_costs.max())

    # Restriction 1: if New York is opened, Los Angeles must be opened too.
    model.addCons(open_warehouse[new_york] <= open_warehouse[los_angeles])

    # Restriction 2: no more than three warehouses are open (the statement's limit of three).
    model.addCons(open_warehouse.sum() <= 3)

    # Restriction 3: Atlanta or Los Angeles must be opened (at least one of them).
    model.addCons(open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1)

    # Every region receives exactly its demand, summed over the warehouses.
    model.addMatrixCons(ships.sum(axis=0) == demands)

    # An open warehouse ships at most its capacity; a closed warehouse ships nothing.
    model.addMatrixCons(ships.sum(axis=1) <= capacity * open_warehouse)

    # total_cost is the opening cost of the open warehouses plus the cost of all units shipped.
    model.addCons(total_cost == open_warehouse @ fixed_costs + (shipping_costs * ships).sum())
    model.setObjective(total_cost, "minimize")

    return model, {"open_warehouse": open_warehouse, "ships": ships, "total_cost": total_cost}


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
