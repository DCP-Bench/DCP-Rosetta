# csplib_024_langford: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_024_langford.py csplib_024_langford.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Arrange two copies of each of the numbers 1 to k in one row of 2k places, so that the two copies of each number i have exactly i numbers between them."""
    k = instance["k"]  # the largest number: each of 1..k appears twice
    length = 2 * k     # the row has one place for each of the 2k copies
    numbers = range(1, k + 1)

    model = gp.Model("langford")

    # starts[i, p] is 1 when the first copy of number i is in place p. The second copy is then in
    # place p + i + 1, which must still be in the row.
    starts = model.addVars([(i, p) for i in numbers for p in range(length - i - 1)],
                           vtype=GRB.BINARY, name="starts")

    # Each number is placed exactly once, as its pair of copies.
    model.addConstrs((starts.sum(i, "*") == 1 for i in numbers), name="place")

    # Every place in the row holds exactly one copy. A placement (i, p) puts copies in place p and
    # in place p + i + 1, so it covers a place q when q is one of those two.
    model.addConstrs((gp.quicksum(starts[i, p] for (i, p) in starts.keys() if q in (p, p + i + 1)) == 1
                      for q in range(length)), name="one_copy_per_place")

    # sol[q] is the number in place q, read from the placements that cover place q.
    sol = [gp.quicksum(i * starts[i, p] for (i, p) in starts.keys() if q in (p, p + i + 1))
           for q in range(length)]
    return model, {"sol": sol}


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
