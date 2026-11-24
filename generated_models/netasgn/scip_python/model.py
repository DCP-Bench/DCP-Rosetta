# netasgn: a SCIP (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python netasgn.py netasgn.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """A project assignment problem. Each person has a number of hours available
    (their supply), and each project needs a number of hours (its demand). A person
    can work on a project for at most a set number of hours, and each hour costs a
    rate that depends on the person and the project. Decide how many hours each
    person works on each project so that every person's available hours and every
    project's required hours are used up exactly, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost of one hour of person i on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i may work on project j

    model = Model("netasgn")

    # assign[i][j] is the number of hours person i works on project j. It is a whole
    # number from 0 (lb=0: hours cannot be negative) up to limit[i][j], the cap the
    # instance gives for that pair. The matrix form takes the shape of the table and
    # reads the per-entry cap from limit, so no index loop is needed.
    assign = model.addMatrixVar((len(supply), len(demand)), vtype="I", lb=0, ub=limit, name="assign")

    # Each person's hours over all projects add up to that person's supply, so all
    # of the person's available hours are assigned.
    model.addMatrixCons(assign.sum(axis=1) == np.array(supply))

    # Each project's hours over all people add up to that project's demand, so the
    # project gets exactly the hours it requires.
    model.addMatrixCons(assign.sum(axis=0) == np.array(demand))

    # total_cost is the cost of all the assigned hours: each person's hours on each
    # project times the cost of that hour.
    total_cost = (np.array(cost) * assign).sum()

    # Minimise the total cost of the assignment.
    model.setObjective(total_cost, "minimize")

    return model, {"assign": assign, "total_cost": total_cost}


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
