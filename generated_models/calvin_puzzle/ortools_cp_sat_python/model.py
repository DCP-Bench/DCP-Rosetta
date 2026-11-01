# calvin_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install ortools`):
#   python calvin_puzzle.py calvin_puzzle.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    cells = n * n      # the number of squares, which is also the largest number

    # The steps from one square to the next: three squares along a row or column, or two
    # squares along a diagonal.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    model = cp_model.CpModel()

    # x[i][j] is the number written in row i, column j
    x = [[model.new_int_var(1, cells, f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # Square (i, j) has the index 1 + i * n + j. Index 0 stands for before square 1 and after square n^2.
    def index(i, j):
        return 1 + i * n + j

    # Every number from 1 to n^2 is used exactly once.
    model.add_all_different([x[i][j] for i in range(n) for j in range(n)])

    # The possible steps of the path, including the start and the end
    arcs = []
    for i in range(n):
        for j in range(n):
            # first[i][j] is true when the path starts at square (i, j), which holds 1.
            first = model.new_bool_var(f"first_{i}_{j}")
            arcs.append((0, index(i, j), first))
            model.add(x[i][j] == 1).only_enforce_if(first)
            # last[i][j] is true when the path ends at square (i, j), which holds n^2.
            last = model.new_bool_var(f"last_{i}_{j}")
            arcs.append((index(i, j), 0, last))
            model.add(x[i][j] == cells).only_enforce_if(last)
            # jump[i][j][a][b] is true when square (a, b) holds the number after the one in square (i, j).
            for di, dj in moves:
                a, b = i + di, j + dj
                if 0 <= a < n and 0 <= b < n:
                    jump = model.new_bool_var(f"jump_{i}_{j}_{a}_{b}")
                    arcs.append((index(i, j), index(a, b), jump))
                    model.add(x[a][b] == x[i][j] + 1).only_enforce_if(jump)

    # The chosen steps link all squares into one path.
    model.add_circuit(arcs)

    return model, {"x": x}


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
