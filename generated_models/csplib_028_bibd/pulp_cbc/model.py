# csplib_028_bibd: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

import itertools

import pulp


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object is
    in exactly r blocks, and every two distinct objects are together in exactly lambda blocks."""
    v = instance["v"]  # the number of objects
    b = instance["b"]  # the number of blocks
    r = instance["r"]  # the number of blocks each object is in
    k = instance["k"]  # the number of objects in each block
    lam = instance["l"]  # the number of blocks in which each pair of objects is together

    problem = pulp.LpProblem("bibd", pulp.LpMinimize)

    # matrix[i][c] is 1 when object i is in block c, and 0 when not.
    matrix = [[pulp.LpVariable(f"matrix_{i}_{c}", cat="Binary") for c in range(b)]
              for i in range(v)]

    # Each object is in exactly r blocks.
    for i in range(v):
        problem += pulp.lpSum(matrix[i]) == r
    # Each block holds exactly k objects.
    for c in range(b):
        problem += pulp.lpSum(matrix[i][c] for i in range(v)) == k

    # both[(i, j)][c] is 1 exactly when objects i and j are both in block c.
    both = {}
    for i, j in itertools.combinations(range(v), 2):
        both[(i, j)] = [pulp.LpVariable(f"both_{i}_{j}_{c}", cat="Binary") for c in range(b)]
        for c in range(b):
            problem += both[(i, j)][c] <= matrix[i][c]
            problem += both[(i, j)][c] <= matrix[j][c]
            problem += both[(i, j)][c] >= matrix[i][c] + matrix[j][c] - 1

    # Each pair of distinct objects is together in exactly lambda blocks.
    for pair in both:
        problem += pulp.lpSum(both[pair]) == lam

    # A block with k objects contains k(k - 1) / 2 pairs of objects.
    for c in range(b):
        problem += pulp.lpSum(both[pair][c] for pair in both) == k * (k - 1) // 2

    # An object in a block shares it with the other k - 1 objects, and an object outside it
    # shares nothing with it.
    for c in range(b):
        for i in range(v):
            problem += pulp.lpSum(
                both[(min(i, j), max(i, j))][c] for j in range(v) if j != i
            ) == (k - 1) * matrix[i][c]

    return problem, {"matrix": matrix}


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
