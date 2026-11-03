# session2_subsets_100: a Z3 (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

import z3


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A whose elements have the same sum."""
    A = instance["A"]  # the integers of the set A, all different
    n_integers = len(A)  # the number of integers in A

    # in_S[i] is true when the i-th integer of A is in S
    in_S = [z3.Bool(f"in_S_{i}") for i in range(n_integers)]
    # in_T[i] is true when the i-th integer of A is in T
    in_T = [z3.Bool(f"in_T_{i}") for i in range(n_integers)]

    solver = z3.Solver()

    # S and T have the same sum.
    solver.add(z3.Sum([z3.If(s, a, 0) for a, s in zip(A, in_S)])
               == z3.Sum([z3.If(t, a, 0) for a, t in zip(A, in_T)]))

    # S and T are disjoint: no integer is in both.
    solver.add([z3.Not(z3.And(s, t)) for s, t in zip(in_S, in_T)])

    # S and T are non-empty.
    solver.add(z3.Or(in_S), z3.Or(in_T))

    return solver, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
