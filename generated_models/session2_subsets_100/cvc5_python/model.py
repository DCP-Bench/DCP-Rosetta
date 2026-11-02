# session2_subsets_100: a cvc5 (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

import cvc5.pythonic as c5


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A such that the elements of S sum to the same value as the
    elements of T."""
    A = instance["A"]    # A[i]: the i-th integer of the set
    n_integers = len(A)  # the number of integers in the set

    # in_S[i] is true when the i-th integer is in S
    in_S = [c5.Bool(f"in_S_{i}") for i in range(n_integers)]
    # in_T[i] is true when the i-th integer is in T
    in_T = [c5.Bool(f"in_T_{i}") for i in range(n_integers)]

    solver = c5.Solver()

    # S and T are disjoint: no integer is in both.
    for s, t in zip(in_S, in_T):
        solver.add(c5.Not(c5.And(s, t)))

    # S and T are non-empty.
    solver.add(c5.Or(in_S))
    solver.add(c5.Or(in_T))

    # S and T have the same sum.
    sum_S = c5.Sum([c5.If(s, a, 0) for s, a in zip(in_S, A)])
    sum_T = c5.Sum([c5.If(t, a, 0) for t, a in zip(in_T, A)])
    solver.add(sum_S == sum_T)

    return solver, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
