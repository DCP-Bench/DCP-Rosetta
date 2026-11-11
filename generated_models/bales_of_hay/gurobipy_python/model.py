# bales_of_hay: a Gurobi (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python bales_of_hay.py bales_of_hay.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Bales of hay: find the weight of each bale, given the weights of every pair of bales, written down in order without saying which pair weighed what."""
    n = instance["n"]                # the number of bales
    weights = instance["weights"]    # the weights of all pairs of bales, in increasing order, without saying which pair weighed what
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]  # every pair of bales, i < j
    written = range(len(weights))    # one index per written pair weight

    model = gp.Model("bales_of_hay")

    # bales[i] is the weight of bale i. The upper bound is not in the statement: weights are not
    # negative, so no bale is heavier than the heaviest pair, and the bound cuts off no solution.
    bales = model.addVars(n, lb=0, ub=max(weights), vtype=GRB.INTEGER, name="bales")

    # matches[k, p] is 1 when written weight k is the weight of pair p.
    matches = model.addVars(written, range(len(pairs)), vtype=GRB.BINARY, name="matches")

    # Each written weight is the weight of exactly one pair.
    model.addConstrs((matches.sum(k, "*") == 1 for k in written), name="weight")
    # Every pair was weighed exactly once, so each pair takes exactly one written weight.
    model.addConstrs((matches.sum("*", p) == 1 for p in range(len(pairs))), name="pair")

    # A written weight matched to a pair is that pair's total weight.
    model.addConstrs(((matches[k, p] == 1) >> (bales[i] + bales[j] == weights[k])
                      for k in written for p, (i, j) in enumerate(pairs)), name="weighs")

    # The weight of each bale, in order.
    return model, {"bales": [bales[i] for i in range(n)]}


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
