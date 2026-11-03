# csplib_003_quasigroup_existence: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import mip


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, an m by m table over the
    values 0 to m-1 in which every value occurs once in each row and each column, with
    (a*b)*(b*a) = a for all a and b."""
    m = instance["m"]  # order of the quasigroup
    vals = range(m)    # the values of the table

    model = mip.Model(solver_name="CBC")

    # The pair (a*b, b*a) of products of a and b. The condition (a*b)*(b*a) = a makes this
    # map its own inverse: if (a, b) maps to (k, l), then (k, l) maps back to (a, b). The
    # pair (b, a) maps to the swap of the image of (a, b). So the four tuples (a,b,k,l),
    # (k,l,a,b), (b,a,l,k) and (l,k,b,a) stand for one fact, and share one variable.
    # Smallest of the four equivalent tuples, used as the key of the shared variable.
    def key(a, b, k, l):
        return min((a, b, k, l), (k, l, a, b), (b, a, l, k), (l, k, b, a))

    # pv[t] is 1 when the pair (a, b) maps to (k, l), for the key t of that fact.
    pv = {}
    for a in vals:
        for b in vals:
            for k in vals:
                for l in vals:
                    t = key(a, b, k, l)
                    if t not in pv:
                        pv[t] = model.add_var(f"p_{t[0]}_{t[1]}_{t[2]}_{t[3]}", var_type=mip.BINARY)

    # The variable for the fact that the pair (a, b) maps to (k, l).
    def p(a, b, k, l):
        return pv[key(a, b, k, l)]

    # x[i][j][v] is 1 when the product i*j is v.
    x = [[[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY) for v in vals]
          for j in vals] for i in vals]
    # q[i][j] is the product i*j as a number.
    q = [[model.add_var(f"q_{i}_{j}", lb=0, ub=m - 1, var_type=mip.INTEGER)
          for j in vals] for i in vals]

    # Each cell of the table holds one value, and q is that value.
    for i in vals:
        for j in vals:
            model += mip.xsum(x[i][j][v] for v in vals) == 1
            model += q[i][j] == mip.xsum(v * x[i][j][v] for v in vals)

    # Each value occurs once in every row.
    for i in vals:
        for v in vals:
            model += mip.xsum(x[i][j][v] for j in vals) == 1

    # Each value occurs once in every column.
    for j in vals:
        for v in vals:
            model += mip.xsum(x[i][j][v] for i in vals) == 1

    # a*b is k exactly when the pair (a, b) maps to a pair whose first entry is k.
    for a in vals:
        for b in vals:
            for k in vals:
                model += x[a][b][k] == mip.xsum(p(a, b, k, l) for l in vals)

    # The map of pairs is a bijection: each pair (k, l) is the image of exactly one pair (a, b).
    for k in vals:
        for l in vals:
            model += mip.xsum(p(a, b, k, l) for a in vals for b in vals) == 1

    # Each pair (a, b) has exactly one image.
    for a in vals:
        for b in vals:
            model += mip.xsum(p(a, b, k, l) for k in vals for l in vals) == 1

    # The squares a*a cover every value once: each value c is a*a for exactly one a.
    for c in vals:
        model += mip.xsum(x[a][a][c] for a in vals) == 1

    return model, {"quasigroup": q}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
