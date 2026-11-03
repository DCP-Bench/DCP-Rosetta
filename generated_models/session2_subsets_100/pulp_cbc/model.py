# session2_subsets_100: a PuLP (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

import pulp


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A such that the elements of S sum to the same value as the
    elements of T."""
    A = instance["A"]  # A[i]: the i-th integer of the set
    n_integers = len(A)  # the number of integers in the set

    problem = pulp.LpProblem("subsets", pulp.LpMinimize)

    # in_S[i] is 1 when the i-th integer of A belongs to S, and 0 when not
    in_S = [pulp.LpVariable(f"in_S_{i}", cat="Binary") for i in range(n_integers)]
    # in_T[i] is 1 when the i-th integer of A belongs to T, and 0 when not
    in_T = [pulp.LpVariable(f"in_T_{i}", cat="Binary") for i in range(n_integers)]

    # S and T have the same sum.
    problem += (pulp.lpSum(A[i] * in_S[i] for i in range(n_integers))
                == pulp.lpSum(A[i] * in_T[i] for i in range(n_integers)))

    # S and T are disjoint: no integer lies in both.
    for i in range(n_integers):
        problem += in_S[i] + in_T[i] <= 1

    # S and T are non-empty.
    problem += pulp.lpSum(in_S) >= 1
    problem += pulp.lpSum(in_T) >= 1

    return problem, {"in_S": in_S, "in_T": in_T}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
