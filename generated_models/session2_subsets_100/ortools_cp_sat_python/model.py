# session2_subsets_100: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install ortools`):
#   python session2_subsets_100.py session2_subsets_100.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A such that the elements of S sum to the same value as the
    elements of T."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n_integers = len(A)  # the number of integers in the set

    model = cp_model.CpModel()

    # in_S[i] is true when the i-th integer of A belongs to S
    in_S = [model.new_bool_var(f"in_S_{i}") for i in range(n_integers)]
    # in_T[i] is true when the i-th integer of A belongs to T
    in_T = [model.new_bool_var(f"in_T_{i}") for i in range(n_integers)]

    # S and T have the same sum.
    model.add(sum(a * s for a, s in zip(A, in_S)) == sum(a * t for a, t in zip(A, in_T)))
    # S and T are disjoint: no integer lies in both.
    for s, t in zip(in_S, in_T):
        model.add_at_most_one([s, t])
    # S and T are non-empty.
    model.add(sum(in_S) >= 1)
    model.add(sum(in_T) >= 1)

    return model, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
