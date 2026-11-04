# netasgn: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install ortools`):
#   python netasgn.py netasgn.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can contribute to project j
    people, projects = len(cost), len(cost[0])  # number of people and projects

    model = cp_model.CpModel()

    # assign[i][j]: the number of hours person i works on project j, up to limit[i][j]
    assign = [[model.new_int_var(0, limit[i][j], f"assign_{i}_{j}")
               for j in range(projects)]
              for i in range(people)]

    # The hours of each person add up to their supply.
    for i in range(people):
        model.add(sum(assign[i]) == supply[i])

    # The hours on each project add up to its demand.
    for j in range(projects):
        model.add(sum(assign[i][j] for i in range(people)) == demand[j])

    # total_cost: the hours times their cost per hour, summed over all pairs
    total_cost = sum(cost[i][j] * assign[i][j]
                     for i in range(people) for j in range(projects))

    # Assign hours at the lowest total cost.
    model.minimize(total_cost)

    return model, {"assign": assign, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
