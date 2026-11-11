# session2_color_simple: a Gurobi (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session2_color_simple.py session2_color_simple.json

import gurobipy as gp
from gurobipy import GRB

# The six countries (Belgium, Denmark, France, Germany, Netherlands,
# Luxembourg) belong to the problem; the reference fixes their number at 6.
NUM_NODES = 6


def create_model(instance):
    """Map colouring: colour six countries so that neighbours differ, using as few colours as possible."""
    graph = instance["graph"]  # graph[k] = [i, j]: countries i and j are neighbours, numbered from 1
    nodes = range(NUM_NODES)
    # Six colours: not in the statement. Six countries never need more colours than that,
    # so it keeps the colour numbers finite.
    colours = range(1, NUM_NODES + 1)

    model = gp.Model("session2_color_simple")

    # paint[i, c] = 1 when country i has colour c.
    paint = model.addVars(nodes, colours, vtype=GRB.BINARY, name="paint")
    # Each country has exactly one colour.
    model.addConstrs((paint.sum(i, "*") == 1 for i in nodes), name="one_colour")
    # colors[i] is the colour number of country i.
    colors = [gp.quicksum(c * paint[i, c] for c in colours) for i in nodes]

    # Two neighbouring countries cannot have the same colour.
    model.addConstrs((paint[i - 1, c] + paint[j - 1, c] <= 1
                      for (i, j) in graph for c in colours), name="neighbours")

    # used is the number of colours used: the largest colour number of any country.
    # Its upper bound of 6 is not in the statement; it is the colour bound above.
    used = model.addVar(lb=1, ub=NUM_NODES, vtype=GRB.INTEGER, name="used")
    # used is at least the colour number of every country.
    model.addConstrs((used >= colors[i] for i in nodes), name="used_covers")
    # Minimise the number of colours used.
    model.setObjective(used, GRB.MINIMIZE)

    return model, {"colors": colors}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
