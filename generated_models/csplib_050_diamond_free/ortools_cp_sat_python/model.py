# csplib_050_diamond_free: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import itertools

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a simple undirected graph on n vertices that is diamond-free (any four
    vertices span at most four edges), where every vertex has a degree that is a
    positive multiple of 3 and the sum of the degrees is a multiple of 12."""
    n = instance["N"]  # the number of vertices

    model = cp_model.CpModel()

    # matrix[i][j] is true when vertices i and j are joined by an edge
    matrix = [[model.new_bool_var(f"matrix_{i}_{j}") for j in range(n)] for i in range(n)]

    # The graph is undirected: an edge from i to j is also an edge from j to i.
    for i in range(n):
        for j in range(i + 1, n):
            model.add(matrix[i][j] == matrix[j][i])
    # The graph is simple: no vertex is joined to itself.
    for i in range(n):
        model.add(matrix[i][i] == 0)

    # Each vertex has a degree that is a positive multiple of 3.
    for i in range(n):
        degree = model.new_int_var(1, n, f"degree_{i}")  # the number of edges at vertex i
        model.add(degree == sum(matrix[i]))
        multiple = model.new_int_var(1, n // 3, f"degree_third_{i}")  # the degree divided by 3
        model.add(degree == 3 * multiple)

    # The sum of the degrees is a multiple of 12. Each edge is counted at both of its ends.
    degree_sum_twelfths = model.new_int_var(0, n * n // 12, "degree_sum_twelfths")  # the sum of the degrees divided by 12
    model.add(sum(cell for row in matrix for cell in row) == 12 * degree_sum_twelfths)

    # Diamond-free: any four vertices span at most four of their six possible edges.
    for a, b, c, d in itertools.combinations(range(n), 4):
        model.add(matrix[a][b] + matrix[a][c] + matrix[a][d]
                  + matrix[b][c] + matrix[b][d] + matrix[c][d] <= 4)

    return model, {"matrix": matrix}


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
