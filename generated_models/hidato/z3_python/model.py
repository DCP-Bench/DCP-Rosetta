# hidato: a Z3 (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python hidato.py hidato.json

import z3


def create_model(instance):
    """Hidato: fill a grid of r rows and c columns with the numbers 1 to r*c, each used once,
    keeping the given numbers, so that every number and the next one sit in cells that touch
    horizontally, vertically or diagonally."""
    puzzle = instance["puzzle"]  # puzzle[i][j] is the given number in cell (i, j), or 0 if the cell is empty
    r = len(puzzle)  # number of rows
    c = len(puzzle[0])  # number of columns
    n = r * c  # the numbers run from 1 to n

    # x[i][j] is the number written in cell (i, j)
    x = [[z3.Int(f"x_{i}_{j}") for j in range(c)] for i in range(r)]

    # Every cell, and the given numbers with the cell they are in
    cells = [(i, j) for i in range(r) for j in range(c)]
    givens = [(puzzle[i][j], (i, j)) for (i, j) in cells if puzzle[i][j] > 0]

    # Two different cells touch when they are one step apart horizontally, vertically or diagonally.
    def touching(a, b):
        return a != b and max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    # Number k can sit in cell p unless p is a given cell holding another number, or p is
    # further from a given number v than the steps k and v are apart, since each step
    # moves to a touching cell.
    def possible(k, p):
        if puzzle[p[0]][p[1]] > 0 and puzzle[p[0]][p[1]] != k:
            return False
        for v, q in givens:
            if max(abs(p[0] - q[0]), abs(p[1] - q[1])) > abs(k - v):
                return False
        return True

    # in_cell[k][p] is true when number k is in cell p, for the cells where k is possible
    in_cell = {k: {p: z3.Bool(f"in_cell_{k}_{p[0]}_{p[1]}") for p in cells if possible(k, p)}
               for k in range(1, n + 1)}

    solver = z3.Solver()

    # Every cell holds a number from 1 to n.
    solver.add([z3.And(1 <= x[i][j], x[i][j] <= n) for (i, j) in cells])

    # If number k is in cell p, then cell p holds k.
    for k in range(1, n + 1):
        solver.add([z3.Implies(w, x[p[0]][p[1]] == k) for p, w in in_cell[k].items()])

    # Each number is in exactly one cell.
    solver.add([z3.PbEq([(w, 1) for w in in_cell[k].values()], 1) if in_cell[k] else z3.BoolVal(False)
                for k in range(1, n + 1)])

    # Each cell holds exactly one number.
    for p in cells:
        holders = [(in_cell[k][p], 1) for k in range(1, n + 1) if p in in_cell[k]]
        solver.add(z3.PbEq(holders, 1) if holders else z3.BoolVal(False))

    # The given numbers are in their cells.
    solver.add([in_cell[v].get(p, z3.BoolVal(False)) for v, p in givens])

    # Each number has the next number in a touching cell, and each number after the first
    # has the number before it in a touching cell.
    for k in range(1, n):
        for p, w in in_cell[k].items():
            solver.add(z3.Implies(w, z3.Or([in_cell[k + 1][q] for q in in_cell[k + 1] if touching(p, q)])))
        for p, w in in_cell[k + 1].items():
            solver.add(z3.Implies(w, z3.Or([in_cell[k][q] for q in in_cell[k] if touching(p, q)])))

    return solver, {"x": x}


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
