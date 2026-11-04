# netasgn: a Python-MIP (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python netasgn.py netasgn.json

import mip


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can contribute to project j
    n_people, n_projects = len(supply), len(demand)  # the number of people and of projects

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # assign[i][j] is the number of hours person i works on project j, up to limit[i][j]
    assign = [
        [model.add_var(f"assign_{i}_{j}", lb=0, ub=limit[i][j], var_type=mip.INTEGER)
         for j in range(n_projects)]
        for i in range(n_people)
    ]

    # Each person works exactly their available hours.
    for i in range(n_people):
        model.add_constr(mip.xsum(assign[i][j] for j in range(n_projects)) == supply[i])

    # Each project gets exactly the hours it requires.
    for j in range(n_projects):
        model.add_constr(mip.xsum(assign[i][j] for i in range(n_people)) == demand[j])

    # Range of the total cost: each pair contributes between 0 and its limit times its cost per hour.
    min_total_cost = sum(min(0, cost[i][j]) * limit[i][j]
                         for i in range(n_people) for j in range(n_projects))
    max_total_cost = sum(max(0, cost[i][j]) * limit[i][j]
                         for i in range(n_people) for j in range(n_projects))

    # total_cost is the cost of all hours assigned.
    total_cost = model.add_var("total_cost", lb=min_total_cost, ub=max_total_cost,
                               var_type=mip.INTEGER)

    # The total cost is the cost per hour of each pair times the hours it works, summed over all pairs.
    model.add_constr(
        total_cost
        == mip.xsum(cost[i][j] * assign[i][j]
                    for i in range(n_people) for j in range(n_projects))
    )

    # Minimise the total cost.
    model.objective = total_cost

    return model, {"assign": assign, "total_cost": total_cost}


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
