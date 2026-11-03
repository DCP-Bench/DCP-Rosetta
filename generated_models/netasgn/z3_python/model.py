# netasgn: a Z3 (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python netasgn.py netasgn.json

import z3


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can work on project j
    n_people, n_projects = len(supply), len(demand)

    # assign[i][j]: the hours person i works on project j
    assign = [[z3.Int(f"assign_{i}_{j}") for j in range(n_projects)] for i in range(n_people)]

    solver = z3.Optimize()

    # Person i works no negative hours on project j, and no more than the limit.
    solver.add([z3.And(assign[i][j] >= 0, assign[i][j] <= limit[i][j])
                for i in range(n_people) for j in range(n_projects)])

    # The hours of each person add up to their supply.
    solver.add([z3.Sum(assign[i]) == supply[i] for i in range(n_people)])

    # The hours on each project add up to its demand.
    solver.add([z3.Sum([assign[i][j] for i in range(n_people)]) == demand[j]
                for j in range(n_projects)])

    # The total cost of all hours, to be as low as possible.
    total_cost = z3.Sum([cost[i][j] * assign[i][j] for i in range(n_people) for j in range(n_projects)])

    solver.minimize(total_cost)

    return solver, {"assign": assign, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
