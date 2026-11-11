# csplib_028_bibd: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_028_bibd.py csplib_028_bibd.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object
    is in exactly r blocks, and every two distinct objects are together in exactly lambda blocks."""
    v = instance["v"]  # the number of objects (rows of the matrix)
    b = instance["b"]  # the number of blocks (columns of the matrix)
    r = instance["r"]  # the number of blocks each object is in
    k = instance["k"]  # the number of objects each block holds
    lam = instance["l"]  # lambda (the field is named "l"): the number of blocks every two distinct objects share

    model = gp.Model("bibd")

    # matrix[i, j] is 1 when object i is in block j
    matrix = model.addVars(v, b, vtype=GRB.BINARY, name="matrix")

    # Each object is in exactly r blocks (matrix.sum(i, "*") adds over the blocks)
    model.addConstrs((matrix.sum(i, "*") == r for i in range(v)), name="object_in_r_blocks")
    # Each block holds exactly k objects (matrix.sum("*", j) adds over the objects)
    model.addConstrs((matrix.sum("*", j) == k for j in range(b)), name="block_holds_k")

    # Each pair of distinct objects, once each
    pairs = [(i1, i2) for i1 in range(v) for i2 in range(i1 + 1, v)]
    # both[i1, i2, j] is 1 when objects i1 and i2 are both in block j
    both = model.addVars([(i1, i2, j) for i1, i2 in pairs for j in range(b)], vtype=GRB.BINARY, name="both")
    # both[i1, i2, j] is the AND of matrix[i1, j] and matrix[i2, j]. Each is one Gurobi AND
    # constraint, because three linear inequalities per product would exceed the pip licence's
    # 2000-constraint limit on the larger instances.
    model.addConstrs((both[i1, i2, j] == gp.and_(matrix[i1, j], matrix[i2, j])
                      for i1, i2 in pairs for j in range(b)), name="both_is_and")
    # Every two distinct objects are together in exactly lambda blocks
    # (both.sum(i1, i2, "*") adds over the blocks)
    model.addConstrs((both.sum(i1, i2, "*") == lam for i1, i2 in pairs), name="pair_shares_lambda")

    # The incidence matrix, as a list of rows of 0s and 1s
    return model, {"matrix": [[matrix[i, j] for j in range(b)] for i in range(v)]}


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
