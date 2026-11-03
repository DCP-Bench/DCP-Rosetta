# session2_subsets_100: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

from pychoco.model import Model


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A whose elements have the same sum. S and T need not together
    cover all of A."""
    A = instance["A"]          # A[i]: the i-th integer of the set
    n_integers = len(A)        # the number of integers in the set

    model = Model()

    # in_S[i] is true when the i-th integer belongs to S
    in_S = [model.boolvar(name=f"in_S_{i}") for i in range(n_integers)]
    # in_T[i] is true when the i-th integer belongs to T
    in_T = [model.boolvar(name=f"in_T_{i}") for i in range(n_integers)]

    # The sum of S equals the sum of T.
    model.scalar(in_S + in_T, A + [-a for a in A], "=", 0).post()

    # No integer belongs to both S and T.
    for i in range(n_integers):
        model.sum([in_S[i], in_T[i]], "<=", 1).post()

    # S and T are non-empty.
    model.sum(in_S, ">=", 1).post()
    model.sum(in_T, ">=", 1).post()

    return model, {"in_S": in_S, "in_T": in_T}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
