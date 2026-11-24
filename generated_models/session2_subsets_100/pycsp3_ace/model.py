# session2_subsets_100: a PyCSP3 model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session2_subsets_100.py session2_subsets_100.json

from pycsp3 import *


def create_model(instance):
    """From a set A of different integers, find two disjoint non-empty subsets S and T of A
    whose elements have the same sum. S union T does not need to be all of A."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n_elements = len(A)

    # in_S[i] is 1 when the element A[i] is in S, and 0 when it is not.
    in_S = VarArray(size=n_elements, dom={0, 1})
    # in_T[i] is 1 when the element A[i] is in T, and 0 when it is not.
    in_T = VarArray(size=n_elements, dom={0, 1})

    satisfy(
        # S and T are disjoint: no element is in both.
        [in_S[i] + in_T[i] <= 1 for i in range(n_elements)],
        # S and T are non-empty.
        Sum(in_S) >= 1,
        Sum(in_T) >= 1,
        # The elements of S and the elements of T have the same sum.
        Sum(A[i] * in_S[i] for i in range(n_elements)) == Sum(A[i] * in_T[i] for i in range(n_elements)),
    )

    return {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
