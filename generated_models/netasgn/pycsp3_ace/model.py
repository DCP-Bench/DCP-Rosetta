# netasgn: a PyCSP3 model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python netasgn.py netasgn.json

from pycsp3 import *


def create_model(instance):
    """Project assignment: each person has a number of available hours and each project requires a
    number of hours. The cost per hour of work for a person on a project is given, and a person can
    contribute to a project up to a limit. Assign the people to the projects at minimum total cost,
    so that each person's hours equal their supply and each project's hours equal its demand."""
    supply = instance["supply"]  # supply[i]: hours available from person i
    demand = instance["demand"]  # demand[j]: hours required by project j
    cost = instance["cost"]      # cost[i][j]: cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: most hours person i can work on project j (an instance field, not in the statement's text)
    n_people = len(supply)
    n_projects = len(demand)

    # assign[i][j] is the number of hours person i works on project j. Hours are taken as non-negative,
    # and an assignment is at most its limit, so at most the largest limit.
    largest_limit = max(max(row) for row in limit)
    assign = VarArray(size=[n_people, n_projects], dom=range(largest_limit + 1))

    # total_cost is the total cost of the assignment. Costs are taken as non-negative, and the hours
    # assigned add up to the total supply, so the cost is at most the largest cost times all the hours.
    largest_cost = max(max(row) for row in cost)
    total_supply = sum(supply)
    total_cost = Var(dom=range(largest_cost * total_supply + 1))

    satisfy(
        # Each person's assigned hours add up to their supply.
        [Sum(assign[i][j] for j in range(n_projects)) == supply[i] for i in range(n_people)],
        # Each project's assigned hours add up to its demand.
        [Sum(assign[i][j] for i in range(n_people)) == demand[j] for j in range(n_projects)],
        # A person works on a project for at most the limit on that pair.
        [assign[i][j] <= limit[i][j] for i in range(n_people) for j in range(n_projects)],
        # The total cost is the cost per hour times the hours worked, summed over all pairs.
        total_cost == Sum(cost[i][j] * assign[i][j] for i in range(n_people) for j in range(n_projects)),
    )

    # Minimise the total cost of the assignment.
    minimize(total_cost)

    return {"assign": assign, "total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("assign", "=")
        for row in outputs["assign"]:
            print(values(row))
    else:
        print("No solution:", status())
