# knights_tour: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install ortools`):
#   python knights_tour.py knights_tour.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    cells = n * n      # the number of squares

    model = cp_model.CpModel()

    # x[i][j] is the move at which the knight visits square (i, j).
    x = [[model.new_int_var(0, cells - 1, f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # Node 0 is the start and end of the tour. Square (i, j) is node 1 + i*n + j.
    def node(i, j):
        return 1 + i * n + j

    # Each square is visited at a different move.
    model.add_all_different([x[i][j] for i in range(n) for j in range(n)])

    # The knight's moves as (row step, column step).
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    # The moves the tour can take, each with a flag for whether the tour uses it.
    arcs = []
    for i in range(n):
        for j in range(n):
            # first[i][j] is true when the tour starts on square (i, j), at move 0
            first = model.new_bool_var(f"first_{i}_{j}")
            arcs.append((0, node(i, j), first))
            model.add(x[i][j] == 0).only_enforce_if(first)

            # last[i][j] is true when the tour ends on square (i, j), at the last move
            last = model.new_bool_var(f"last_{i}_{j}")
            arcs.append((node(i, j), 0, last))
            model.add(x[i][j] == cells - 1).only_enforce_if(last)

            # jump[i][j][a][b] is true when the knight goes from square (i, j) to square (a, b)
            # with one knight's move. The move number then goes up by one.
            for di, dj in knight_moves:
                a, b = i + di, j + dj
                if 0 <= a < n and 0 <= b < n:
                    jump = model.new_bool_var(f"jump_{i}_{j}_{a}_{b}")
                    arcs.append((node(i, j), node(a, b), jump))
                    model.add(x[a][b] == x[i][j] + 1).only_enforce_if(jump)

    # Every square is left once and entered once, so the moves form one circuit through node 0.
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
