# csplib_005_autocorrelation: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A binary sequence of length n with minimum periodic energy (CSPLib 005, autocorrelation).

    The sequence S_0, ..., S_{n-1} has n bits, each +1 or -1. With periodic (cyclic) boundary
    conditions its k-th autocorrelation is C_k = sum over i of S_i * S_{(i+k) mod n}, for
    k = 1, ..., n-1. The energy E = sum over k of C_k^2 is to be minimised.
    """
    n = instance["n"]  # the length of the sequence (instance field n)

    model = Model("autocorrelation")

    # b[i] is 1 when bit S_i is +1, and 0 when S_i is -1
    b = [model.addVar(name=f"b_{i}", vtype="B") for i in range(n)]

    # same[i, j] for i < j is 1 when bits i and j are equal, so S_i * S_j is +1 then and -1 otherwise.
    # SCIP has no equality test between two variables, so the xor constraint states it: b_i xor b_j
    # xor same must be 1, which holds exactly when b_i == b_j.
    same = {}
    for i in range(n):
        for j in range(i + 1, n):
            same[i, j] = model.addVar(name=f"same_{i}_{j}", vtype="B")
            model.addConsXor([b[i], b[j], same[i, j]], True)

    # sq[k] is C_k squared, which the linear objective needs. The constraint sq[k] >= C_k * C_k
    # is a quadratic one. Nothing forces sq[k] down to C_k^2 except the minimisation, so sq[k]
    # equals C_k^2 in every optimal solution, not in every feasible one.
    sq = {}
    for k in range(1, n):
        # the n products S_i * S_{(i+k) mod n}, each +1 or -1 as 2 * same - 1; the pair
        # {i, (i+k) mod n} is stored under its smaller index first
        products = []
        for i in range(n):
            j = (i + k) % n
            products.append(2 * same[min(i, j), max(i, j)] - 1)

        # C_k is the sum of n terms that are each -1 or 1, so it lies between -n and n
        c_k = model.addVar(name=f"C_{k}", vtype="I", lb=-n, ub=n)
        model.addCons(c_k == quicksum(products))

        # C_k is at most n in absolute value, so C_k squared is at most n * n
        sq[k] = model.addVar(name=f"C_sq_{k}", vtype="I", lb=0, ub=n * n)
        model.addCons(sq[k] >= c_k * c_k)

    # the energy: the sum of the squared autocorrelations, to be minimised
    model.setObjective(quicksum(sq.values()), "minimize")

    # the output: bit i of the sequence as +1 or -1
    sequence = [2 * bi - 1 for bi in b]
    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
