# session2_subsets_100: an Exact (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

from exact import Exact


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A such that the elements of S sum to the same value as the
    elements of T."""
    A = instance["A"]  # the given integers
    n = len(A)  # how many integers there are

    solver = Exact()

    # Exact identifies its variables by name.
    # in_S[i] is 1 when the integer A[i] is in S, and in_T[i] is 1 when it is in T; 0 when not
    in_S = [f"in_S_{i}" for i in range(n)]
    in_T = [f"in_T_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(in_S[i], 0, 1)
        solver.addVariable(in_T[i], 0, 1)

    # S and T have the same sum.
    solver.addConstraint([(A[i], in_S[i]) for i in range(n) if A[i]]
                         + [(-A[i], in_T[i]) for i in range(n) if A[i]],
                         True, 0, True, 0)

    # S and T are disjoint: no integer is in both.
    for i in range(n):
        solver.addConstraint([(1, in_S[i]), (1, in_T[i])], False, 0, True, 1)

    # S and T are non-empty.
    solver.addConstraint([(1, name) for name in in_S], True, 1)
    solver.addConstraint([(1, name) for name in in_T], True, 1)

    return solver, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
