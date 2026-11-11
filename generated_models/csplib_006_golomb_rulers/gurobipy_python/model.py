# csplib_006_golomb_rulers: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A Golomb ruler places marks at whole-number positions, the first at 0, so that the distances between every two marks are all different. Find the shortest ruler with a given number of marks."""
    size = instance["size"]  # number of marks on the ruler
    mark_ids = range(size)
    # pairs (i, j) with i < j: the two marks that a distance is measured between
    pairs = [(i, j) for i in mark_ids for j in mark_ids if i < j]

    model = gp.Model("golomb_rulers")

    # marks[i] is the position of mark i, a whole number. The upper bound size * size is not from
    # the statement: it is chosen to keep every position finite.
    marks = model.addVars(mark_ids, lb=0, ub=size * size, vtype=GRB.INTEGER, name="marks")

    # The first mark is at 0, and each mark lies strictly to the right of the one before it.
    model.addConstr(marks[0] == 0, name="first_at_zero")
    model.addConstrs((marks[i + 1] >= marks[i] + 1 for i in range(size - 1)), name="increasing")

    # Redundant, not in the statement: marks i < j are at least 1 + 2 + ... + (j - i) apart, since
    # the j - i gaps between consecutive marks from i to j are distinct positive whole numbers
    # (the all-different constraint below implies this). Added only to give the solver a bound.
    model.addConstrs((marks[j] - marks[i] >= (j - i) * (j - i + 1) // 2 for i, j in pairs), name="min_distance")

    # All distances are different: for two pairs (i, j) and (k, l), marks[j] - marks[i] and
    # marks[l] - marks[k] differ. Pairs sharing a lower mark or an upper mark always differ, so
    # only the other pairs are posted. larger[i, j, k, l] is 1 when the distance (i, j) is the
    # longer one, and an indicator then enforces a gap of at least 1 in that direction.
    quads = [(i, j, k, l) for (i, j) in pairs for (k, l) in pairs if (i, j) < (k, l) and i != k and j != l]
    larger = model.addVars(quads, vtype=GRB.BINARY, name="larger")
    model.addConstrs(((larger[i, j, k, l] == 1) >> (marks[j] - marks[i] - (marks[l] - marks[k]) >= 1)
                      for i, j, k, l in quads), name="gt")
    model.addConstrs(((larger[i, j, k, l] == 0) >> (marks[j] - marks[i] - (marks[l] - marks[k]) <= -1)
                      for i, j, k, l in quads), name="lt")

    # Objective: the shortest ruler, whose length is the position of its last mark.
    length = marks[size - 1]
    model.setObjective(length, GRB.MINIMIZE)

    return model, {"marks": [marks[i] for i in mark_ids], "length": length}


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
