# netasgn: a hermax (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install hermax`):
#   python netasgn.py netasgn.json

from hermax.model import Model


def create_model(instance):
    """Project assignment: split the available hours of each person across the projects so
    that every person's supply is used up, every project gets exactly its demanded hours, no
    person works more than the limit on a given project, and the total cost is as small as
    possible."""
    supply = instance["supply"]   # supply[i]: total hours person i is available
    demand = instance["demand"]   # demand[j]: total hours project j needs
    cost = instance["cost"]       # cost[i][j]: cost per hour of person i working on project j
    limit = instance["limit"]     # limit[i][j]: most hours person i may work on project j
    n_people = len(supply)  # number of people
    n_projects = len(demand)  # number of projects

    m = Model()

    # assign[i][j] is the number of hours person i works on project j,
    # between 0 and that pair's limit (each variable gets its own tight domain)
    assign = [
        [m.int(f"assign_{i}_{j}", 0, limit[i][j]) for j in range(n_projects)]
        for i in range(n_people)
    ]

    # Each person's hours across all projects add up exactly to their supply.
    for i in range(n_people):
        m &= (sum(assign[i][j] for j in range(n_projects)) == supply[i])

    # Each project's hours across all people add up exactly to its demand.
    for j in range(n_projects):
        m &= (sum(assign[i][j] for i in range(n_people)) == demand[j])

    # Minimise the total cost: every hour of person i on project j costs cost[i][j].
    total_cost = sum(cost[i][j] * assign[i][j]
                     for i in range(n_people) for j in range(n_projects))
    m.obj += total_cost

    return m, {"assign": assign, "total_cost": total_cost}


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
