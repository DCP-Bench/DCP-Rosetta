# finding_celebrities: a Gurobi (Python) model from DCP Rosetta.
# Download the `finding_celebrities.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python finding_celebrities.py finding_celebrities.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find the celebrities at a party: people whom everybody knows and who know only other celebrities; at least one is present."""
    graph = instance["graph"]  # graph[i][j] is 1 when person i knows person j, and 0 when not
    n = len(graph)             # the number of people at the party
    people = range(n)
    # known_by[i]: how many people know person i (counting i itself when graph[i][i] is 1)
    known_by = [sum(graph[j][i] for j in people) for i in people]
    # knows[i]: how many people person i knows (counting i itself when graph[i][i] is 1)
    knows = [sum(graph[i][j] for j in people) for i in people]

    model = gp.Model("finding_celebrities")

    # celebrities[i] is 1 when person i is a celebrity, and 0 when not.
    celebrities = model.addVars(people, vtype=GRB.BINARY, name="celebrities")

    # count[c] is 1 when there are exactly c celebrities, for c from 1 to n (at least one is present).
    count = model.addVars(range(1, n + 1), vtype=GRB.BINARY, name="count")
    # Exactly one number of celebrities is chosen.
    model.addConstr(count.sum() == 1, name="one_count")
    # The number of celebrities is the chosen count.
    model.addConstr(celebrities.sum() == gp.quicksum(c * count[c] for c in count), name="counted")

    # A person is a celebrity exactly when everybody knows them and they know as many people as there are
    # celebrities (they know only the celebrities, and know themselves through the diagonal).
    # The known_by test and the bounds on knows[i] are fixed by the data, so people who fail them are ruled out
    # with an upper bound of 0; knows[i] must be at least 1 only to index count, which starts at 1.
    for i in people:
        if known_by[i] == n and 1 <= knows[i] <= n:
            model.addConstr(celebrities[i] == count[knows[i]], name=f"celebrity[{i}]")
        else:
            celebrities[i].UB = 0

    # celebrities[i] for each person i, in the order of the input
    return model, {"celebrities": [celebrities[i] for i in people]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
