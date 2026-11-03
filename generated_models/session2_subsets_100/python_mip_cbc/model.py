# session2_subsets_100: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

import mip


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets S
    and T of A whose elements have the same sum."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n = len(A)  # the number of integers in the set

    model = mip.Model(solver_name="CBC")

    # in_S[i] is 1 when the i-th integer is in S, and 0 when not
    in_S = [model.add_var(f"in_S_{i}", var_type=mip.BINARY) for i in range(n)]
    # in_T[i] is 1 when the i-th integer is in T, and 0 when not
    in_T = [model.add_var(f"in_T_{i}", var_type=mip.BINARY) for i in range(n)]

    # No integer is in both S and T.
    for i in range(n):
        model.add_constr(in_S[i] + in_T[i] <= 1)

    # S and T are both non-empty.
    model.add_constr(mip.xsum(in_S) >= 1)
    model.add_constr(mip.xsum(in_T) >= 1)

    # S and T have the same sum.
    model.add_constr(mip.xsum(A[i] * in_S[i] for i in range(n)) == mip.xsum(A[i] * in_T[i] for i in range(n)))

    return model, {"in_S": in_S, "in_T": in_T}


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
