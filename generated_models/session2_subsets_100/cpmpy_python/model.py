# session2_subsets_100: a CPMpy model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session2_subsets_100.py session2_subsets_100.json

import cpmpy as cp


def create_model(instance):
    """Given a list of different integers A, find two disjoint non-empty subsets
    S and T of A such that the sum of the elements in S equals the sum of the
    elements in T."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n = len(A)

    # in_S[i] is true when element i belongs to subset S
    in_S = cp.boolvar(shape=n, name="in_S")
    # in_T[i] is true when element i belongs to subset T
    in_T = cp.boolvar(shape=n, name="in_T")

    model = cp.Model()
    # S and T have the same sum.
    model.add(cp.sum(in_S * A) == cp.sum(in_T * A))
    # S and T are disjoint: no element lies in both.
    model.add(in_S + in_T <= 1)
    # S and T are non-empty.
    model.add(cp.sum(in_S) > 0)
    model.add(cp.sum(in_T) > 0)

    return model, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
