# csplib_005_autocorrelation: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

import mip


def create_model(instance):
    """Choose a sequence of n values, each +1 or -1, that minimises the sum of the
    squared periodic autocorrelations C_k, where C_k is the sum over i of S_i times
    S_((i+k) mod n), for k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i] is 1 when position i holds +1, and 0 when it holds -1
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]
    # S[i] is the value at position i, +1 or -1
    S = [2 * x[i] - 1 for i in range(n)]

    # w[(i, j)] is 1 when positions i and j both hold +1, one per pair of positions
    products = {}

    def product(i, j):
        key = (min(i, j), max(i, j))
        if key not in products:
            w = model.add_var(f"w_{key[0]}_{key[1]}", var_type=mip.BINARY)
            # w is 1 exactly when both positions hold +1.
            model.add_constr(w <= x[key[0]])
            model.add_constr(w <= x[key[1]])
            model.add_constr(w >= x[key[0]] + x[key[1]] - 1)
            products[key] = w
        return products[key]

    # energy: the squared autocorrelation C_k for each shift k = 1 to n-1
    energy = []
    for k in range(1, n):
        # terms: the product of each position with the one k steps ahead, wrapping around
        terms = []
        for i in range(n):
            j = (i + k) % n
            w = product(i, j)
            # S_i times S_j, which is +1 when the two positions agree and -1 otherwise
            terms.append(4 * w - 2 * x[i] - 2 * x[j] + 1)
        c_k = mip.xsum(terms)

        # The possible values of C_k: a sum of n terms, each +1 or -1.
        values = list(range(-n, n + 1, 2))
        # pick[v] is 1 when C_k equals v.
        pick = {}
        for idx, v in enumerate(values):
            pick[v] = model.add_var(f"pick_{k}_{idx}", var_type=mip.BINARY)
        # C_k takes exactly one of its possible values.
        model += mip.xsum(pick.values()) == 1
        # The chosen value is the autocorrelation C_k.
        model += c_k == mip.xsum(v * pick[v] for v in values)
        energy.append(mip.xsum(v * v * pick[v] for v in values))

    # Minimise the sum of the squared autocorrelations.
    model.objective = mip.xsum(energy)

    # The output is the sequence S_0 to S_(n-1).
    return model, {"sequence": S}


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
