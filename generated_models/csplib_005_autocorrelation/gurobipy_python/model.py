# csplib_005_autocorrelation: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find a binary sequence of n bits, each +1 or -1, whose periodic autocorrelations have the smallest sum of squares."""
    n = instance["n"]  # length of the sequence
    places = range(n)

    model = gp.Model("autocorrelation")

    # up[i] is 1 when bit i is +1 and 0 when it is -1; a bit takes only these two values.
    up = model.addVars(places, vtype=GRB.BINARY, name="up")
    # sequence[i] is the i-th bit, +1 or -1.
    sequence = [2 * up[i] - 1 for i in places]

    # differ[i, j] is 1 when bits i and j have opposite signs, so that the product
    # sequence[i] * sequence[j] equals 1 - 2 * differ[i, j]. The four rows below make
    # differ the exclusive or of up[i] and up[j], without multiplying two variables.
    differ = {}
    for i in places:
        for j in range(i + 1, n):
            d = model.addVar(vtype=GRB.BINARY, name=f"differ[{i},{j}]")
            model.addConstr(d <= up[i] + up[j], name=f"xor_a[{i},{j}]")
            model.addConstr(d <= 2 - up[i] - up[j], name=f"xor_b[{i},{j}]")
            model.addConstr(d >= up[i] - up[j], name=f"xor_c[{i},{j}]")
            model.addConstr(d >= up[j] - up[i], name=f"xor_d[{i},{j}]")
            differ[i, j] = d

    # The periodic autocorrelation at shift s is the sum over i of sequence[i] * sequence[(i+s) mod n],
    # which is n - 2 * (the number of opposite-sign pairs among those n pairs). Shifts s and n - s use
    # exactly the same pairs, so they share one count and one table of squared values.
    energy_terms = []
    count_of = {}
    for s in range(1, n):
        rep = min(s, n - s)
        if rep not in count_of:
            opposite = gp.quicksum(differ[min(i, (i + rep) % n), max(i, (i + rep) % n)] for i in places)
            # pick[rep, k] is 1 when exactly k of the pairs at shift rep have opposite signs. Then the
            # squared autocorrelation (n - 2k)^2 is a constant for that k, so the energy stays linear.
            pick = model.addVars(range(n + 1), vtype=GRB.BINARY, name=f"pick[{rep}]")
            # Exactly one count k is picked for each shift.
            model.addConstr(pick.sum() == 1, name=f"one_count[{rep}]")
            # The number of opposite-sign pairs equals the picked count k.
            model.addConstr(opposite == gp.quicksum(k * pick[k] for k in range(n + 1)), name=f"count[{rep}]")
            count_of[rep] = gp.quicksum((n - 2 * k) ** 2 * pick[k] for k in range(n + 1))
        energy_terms.append(count_of[rep])

    # Minimise E, the sum over all shifts k = 1 .. n-1 of the squared periodic autocorrelation C_k^2.
    model.setObjective(gp.quicksum(energy_terms), GRB.MINIMIZE)

    return model, {"sequence": sequence}


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
