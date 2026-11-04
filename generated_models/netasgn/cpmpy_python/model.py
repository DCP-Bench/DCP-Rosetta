# netasgn: a CPMpy model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python netasgn.py netasgn.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = np.array(instance["supply"])  # supply[i]: the hours person i has available
    demand = np.array(instance["demand"])  # demand[j]: the hours project j requires
    cost = np.array(instance["cost"])      # cost[i][j]: the cost per hour of person i working on project j
    limit = np.array(instance["limit"])    # limit[i][j]: the most hours person i can contribute to project j
    people, projects = cost.shape

    # assign[i, j] is the number of hours person i works on project j;
    # no person gives more hours to a project than the largest limit.
    assign = cp.intvar(0, limit.max(), shape=(people, projects), name="assign")

    # total_cost is the cost of all assigned hours; it is at most the cost of every
    # person working the limit on every project.
    total_cost = cp.intvar(0, (limit * cost).sum(), name="total_cost")

    model = cp.Model()
    # The hours of each person add up to their supply.
    model.add(assign.sum(axis=1) == supply)
    # The hours on each project add up to its demand.
    model.add(assign.sum(axis=0) == demand)
    # A person contributes at most their limit to each project.
    model.add(assign <= limit)
    # The total cost is the sum of hours times their cost per hour.
    model.add(total_cost == cp.sum(assign * cost))
    # Assign hours at the lowest total cost.
    model.minimize(total_cost)

    return model, {"assign": assign, "total_cost": total_cost}


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
