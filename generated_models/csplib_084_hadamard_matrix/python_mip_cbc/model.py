# csplib_084_hadamard_matrix: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

import mip


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]  # length of each sequence, an odd positive integer
    m = (l - 1) // 2   # number of shifts that are constrained

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # The entries of one sequence, each -1 or +1. x[i] is 1 when entry i is +1, and 0 when
    # it is -1, so the entry is 2 * x[i] - 1.
    def sequence(name):
        x = [model.add_var(f"{name}_x{i}", var_type=mip.BINARY) for i in range(l)]
        return x, [2 * xi - 1 for xi in x]

    # A variable for whether two entries have different signs.
    def disagree(u, v, name):
        e = model.add_var(name, var_type=mip.BINARY)
        # e is 1 exactly when u and v differ, and 0 when they match.
        model.add_constr(e >= u - v)
        model.add_constr(e >= v - u)
        model.add_constr(e <= u + v)
        model.add_constr(e + u + v <= 2)
        return e

    xa, a = sequence("a")
    xb, b = sequence("b")

    # Sequence a sums to 1.
    model += mip.xsum(a) == 1

    # Sequence b sums to 1.
    model += mip.xsum(b) == 1

    # For each shift s, the periodic autocorrelations of a and b at s add up to -2. The
    # autocorrelation of a sequence at shift s is l minus twice its number of differing
    # pairs, so the two add up to -2 when the differing pairs of a and b total l + 1.
    for s in range(1, m + 1):
        # da[i] and db[i]: whether entry i differs in sign from entry i + s (mod l), in a and in b
        da = [disagree(xa[i], xa[(i + s) % l], f"da_{s}_{i}") for i in range(l)]
        db = [disagree(xb[i], xb[(i + s) % l], f"db_{s}_{i}") for i in range(l)]
        model += mip.xsum(da + db) == l + 1

    return model, {"a": a, "b": b}


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
