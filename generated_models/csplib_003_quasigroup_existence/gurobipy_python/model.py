# csplib_003_quasigroup_existence: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find an order-m quasigroup: an m-by-m table in which every element occurs once in each row and each column, and (a*b)*(b*a) = a for all a and b (the QG3 problem)."""
    m = instance["m"]  # the order m: the table is m by m, with elements 0 to m-1
    elems = range(m)

    model = gp.Model("quasigroup_qg3")
    # A satisfaction problem: search for a feasible table first.
    model.Params.MIPFocus = 1

    # is_[a, b, c] is 1 when a * b = c in the table.
    is_ = model.addVars(elems, elems, elems, vtype=GRB.BINARY, name="is")
    # product[a][b] is the entry a * b of the table.
    product = [[gp.quicksum(c * is_[a, b, c] for c in elems) for b in elems] for a in elems]

    # Every cell of the table holds exactly one element (is_.sum(a, b, "*") adds over the c's).
    model.addConstrs((is_.sum(a, b, "*") == 1 for a in elems for b in elems), name="cell")

    # Each element occurs once in every row (is_.sum(a, "*", c) adds over the columns b) ...
    model.addConstrs((is_.sum(a, "*", c) == 1 for a in elems for c in elems), name="row")
    # ... and once in every column (is_.sum("*", b, c) adds over the rows a).
    model.addConstrs((is_.sum("*", b, c) == 1 for b in elems for c in elems), name="col")

    # column_of[u][a] is the element w with u * w = a, i.e. the column in which row u holds a.
    column_of = [[gp.quicksum(w * is_[u, w, a] for w in elems) for a in elems] for u in elems]
    # row_of[w][a] is the element u with u * w = a, i.e. the row in which column w holds a.
    row_of = [[gp.quicksum(u * is_[u, w, a] for u in elems) for a in elems] for w in elems]

    # QG3 property (a * b) * (b * a) = a. Let u = a * b; then b * a must be the w with u * w = a,
    # which is column_of[u][a]. One indicator constraint per (a, b, u).
    model.addConstrs(((is_[a, b, u] == 1) >> (product[b][a] == column_of[u][a])
                      for a in elems for b in elems for u in elems), name="qg3")

    # Redundant (not in the statement): the same QG3 property read from the other factor. Let
    # w = b * a; then a * b must be the u with u * w = a, which is row_of[w][a]. It adds nothing
    # to the constraints above and is kept only to help the solver reason from either side.
    model.addConstrs(((is_[b, a, w] == 1) >> (product[a][b] == row_of[w][a])
                      for a in elems for b in elems for w in elems), name="qg3_back")

    # No objective: any table that meets the constraints is a solution.
    # The quasigroup is the table of entries a * b.
    return model, {"quasigroup": product}


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
