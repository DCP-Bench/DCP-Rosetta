# csplib_084_hadamard_matrix: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Hadamard matrix Legendre pairs: find two sequences a and b of l entries, each entry -1 or +1,
    where each sequence sums to 1 and the periodic autocorrelations of a and b add up to -2 at every shift."""
    l = instance["l"]         # the length of each sequence (odd)
    m = (l - 1) // 2          # the number of shifts s = 1..m that the autocorrelation condition covers, from the statement
    idx = range(l)            # positions 0 to l - 1 in each sequence

    model = gp.Model("hadamard_matrix")

    # up_a[i] is 1 when a[i] is +1, and 0 when a[i] is -1; up_b likewise for b.
    up_a = model.addVars(idx, vtype=GRB.BINARY, name="up_a")
    up_b = model.addVars(idx, vtype=GRB.BINARY, name="up_b")
    # Entries are -1 or +1: a[i] = 2 * up_a[i] - 1. A product of two entries is not linear, so the
    # autocorrelations below are written through the 0/1 variables instead.
    a = [2 * up_a[i] - 1 for i in idx]
    b = [2 * up_b[i] - 1 for i in idx]

    # Each sequence sums to 1.
    model.addConstr(gp.quicksum(a) == 1, name="sum_a")
    model.addConstr(gp.quicksum(b) == 1, name="sum_b")

    # PAF(A, s) + PAF(B, s) = -2 for each shift s = 1..m, with positions taken mod l.
    for s in range(1, m + 1):
        # The product of two entries is +1 when they agree and -1 when they differ, so
        # PAF(A, s) = l - 2 * (number of i where a[i] differs from a[(i + s) mod l]).
        # differ_a[i] is 1 when a[i] and a[(i + s) mod l] differ, stated as four linear inequalities
        # (differ_a[i] equals the XOR of up_a[i] and up_a[(i + s) mod l]).
        nxt = [(i + s) % l for i in idx]
        differ_a = model.addVars(idx, vtype=GRB.BINARY, name=f"differ_a[{s}]")
        differ_b = model.addVars(idx, vtype=GRB.BINARY, name=f"differ_b[{s}]")
        for up, differ, tag in ((up_a, differ_a, "a"), (up_b, differ_b, "b")):
            model.addConstrs((differ[i] >= up[i] - up[nxt[i]] for i in idx), name=f"xor1_{tag}[{s}]")
            model.addConstrs((differ[i] >= up[nxt[i]] - up[i] for i in idx), name=f"xor2_{tag}[{s}]")
            model.addConstrs((differ[i] <= up[i] + up[nxt[i]] for i in idx), name=f"xor3_{tag}[{s}]")
            model.addConstrs((differ[i] <= 2 - up[i] - up[nxt[i]] for i in idx), name=f"xor4_{tag}[{s}]")

        paf_a = l - 2 * differ_a.sum()  # differ_a.sum() adds over all positions
        paf_b = l - 2 * differ_b.sum()
        model.addConstr(paf_a + paf_b == -2, name=f"paf[{s}]")

    # There is no objective: any pair of sequences that meets the conditions is a solution.

    # The two sequences, as lists of -1 and +1 entries.
    return model, {"a": a, "b": b}


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
