# netasgn: a PuLP (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python netasgn.py netasgn.json

import pulp


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can work on project j

    n_people = len(supply)    # number of people
    n_projects = len(demand)  # number of projects
    people, projects = range(n_people), range(n_projects)

    problem = pulp.LpProblem("netasgn", pulp.LpMinimize)

    # assign[i][j]: the hours person i works on project j, from 0 up to limit[i][j]
    assign = [[pulp.LpVariable(f"assign_{i}_{j}", 0, limit[i][j], cat="Integer")
               for j in projects]
              for i in people]

    # Each person works exactly their available hours.
    for i in people:
        problem += pulp.lpSum(assign[i]) == supply[i]

    # Each project gets exactly the hours it requires.
    for j in projects:
        problem += pulp.lpSum(assign[i][j] for i in people) == demand[j]

    # Total cost of all hours, each hour at its person's cost per hour. It is minimised.
    total_cost = pulp.lpSum(cost[i][j] * assign[i][j] for i in people for j in projects)
    problem += total_cost

    return problem, {"assign": assign, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
