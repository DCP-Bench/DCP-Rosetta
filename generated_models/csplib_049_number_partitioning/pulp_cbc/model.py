# csplib_049_number_partitioning: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import pulp


def create_model(instance):
    """Split the numbers 1 to n into two sets A and B of the same size, with the same sum and
    the same sum of squares."""
    n = instance["n"]              # the numbers 1 to n are split, n is even
    n_per_set = n // 2             # the number of elements in each set
    numbers = range(1, n + 1)      # the numbers to split

    problem = pulp.LpProblem("number_partitioning", pulp.LpMinimize)  # the puzzle asks for the sets only: no objective

    # in_a[v - 1] is 1 when the number v is in set A, and 0 when it is in set B.
    in_a = [pulp.LpVariable(f"in_a_{v}", cat="Binary") for v in numbers]

    # The two sets have the same number of elements.
    problem += pulp.lpSum(in_a) == n_per_set

    # The two sets have the same sum.
    problem += pulp.lpSum(v * in_a[v - 1] for v in numbers) == pulp.lpSum(
        v * (1 - in_a[v - 1]) for v in numbers)

    # The two sets have the same sum of squares.
    problem += pulp.lpSum(v * v * in_a[v - 1] for v in numbers) == pulp.lpSum(
        v * v * (1 - in_a[v - 1]) for v in numbers)

    # a_has[i][v] is 1 when place i of the list A holds the number v, and 0 when not. b_has is the same for B.
    a_has = pulp.LpVariable.dicts("a_has", (range(n_per_set), numbers), cat="Binary")
    b_has = pulp.LpVariable.dicts("b_has", (range(n_per_set), numbers), cat="Binary")
    # A[i] and B[i] are the numbers in place i of the lists A and B.
    A = [pulp.LpVariable(f"A_{i}", 1, n, cat="Integer") for i in range(n_per_set)]
    B = [pulp.LpVariable(f"B_{i}", 1, n, cat="Integer") for i in range(n_per_set)]

    # Each place of A and each place of B holds exactly one number.
    for i in range(n_per_set):
        problem += pulp.lpSum(a_has[i][v] for v in numbers) == 1
        problem += pulp.lpSum(b_has[i][v] for v in numbers) == 1
        problem += A[i] == pulp.lpSum(v * a_has[i][v] for v in numbers)
        problem += B[i] == pulp.lpSum(v * b_has[i][v] for v in numbers)

    # Each number of A sits in exactly one place of A, each number of B in exactly one place of B,
    # and no number sits in the list of the set it is not in.
    for v in numbers:
        problem += pulp.lpSum(a_has[i][v] for i in range(n_per_set)) == in_a[v - 1]
        problem += pulp.lpSum(b_has[i][v] for i in range(n_per_set)) == 1 - in_a[v - 1]

    return problem, {"A": A, "B": B}


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
