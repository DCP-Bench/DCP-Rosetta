# netasgn: an Exact (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python netasgn.py netasgn.json

from exact import Exact


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can contribute to project j
    people, projects = len(supply), len(demand)

    solver = Exact()

    # Exact identifies its variables by name.
    # assign[i][j] is the number of hours person i works on project j, from 0 up to limit[i][j]
    assign = [[f"h{i}_{j}" for j in range(projects)] for i in range(people)]
    for i in range(people):
        for j in range(projects):
            solver.addVariable(assign[i][j], 0, limit[i][j])

    # Person i works all of their available hours.
    for i in range(people):
        solver.addConstraint([(1, name) for name in assign[i]], True, supply[i], True, supply[i])

    # Project j gets exactly the hours it requires.
    for j in range(projects):
        solver.addConstraint([(1, assign[i][j]) for i in range(people)],
                             True, demand[j], True, demand[j])

    # total_cost is the cost of all hours worked; it is at most the cost of every person
    # working up to their limit on every project.
    ceiling = sum(cost[i][j] * limit[i][j] for i in range(people) for j in range(projects))
    solver.addVariable("total_cost", 0, ceiling)

    # total_cost is the sum of the hours worked times their cost per hour.
    terms = [(cost[i][j], assign[i][j]) for i in range(people) for j in range(projects)]
    solver.addConstraint(terms + [(-1, "total_cost")], True, 0, True, 0)

    # Minimise the total cost.
    solver.setObjective([(1, "total_cost")], minimize=True)

    return solver, {"assign": assign, "total_cost": "total_cost"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
