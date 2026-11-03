# session1_magic_square: a cvc5 (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session1_magic_square.py session1_magic_square.json

import cvc5.pythonic as c5


def exactly_one(flags):
    # Exactly one of the flags is true.
    if len(flags) == 1:
        return [flags[0]]
    out = [c5.Or(flags)]
    for a in range(len(flags)):
        for b in range(a + 1, len(flags)):
            out.append(c5.Or(c5.Not(flags[a]), c5.Not(flags[b])))
    return out


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n^2 so that every row, column and
    diagonal adds up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square
    n_cells = n * n

    # Each row, column and diagonal adds up to n * (n^2 + 1) / 2: the numbers 1 to n^2
    # total n^2 * (n^2 + 1) / 2, shared equally between n rows.
    magic_sum = n * (n_cells + 1) // 2

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # square[i][j] is the number in row i, column j
    square = [[c5.Int(f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # placed[i][j][k] is true when cell (i, j) holds the number k + 1
    placed = [[[c5.Bool(f"placed_{i}_{j}_{k}") for k in range(n_cells)]
               for j in range(n)] for i in range(n)]

    # all n^2 cells of the square
    cells = [square[i][j] for i in range(n) for j in range(n)]

    # Each cell holds exactly one number.
    for i in range(n):
        for j in range(n):
            solver.add(*exactly_one(placed[i][j]))

    # Each number from 1 to n^2 sits in exactly one cell.
    for k in range(n_cells):
        solver.add(*exactly_one([placed[i][j][k] for i in range(n) for j in range(n)]))

    # The number in each cell is the one its flags stand for.
    for i in range(n):
        for j in range(n):
            for k in range(n_cells):
                solver.add(c5.Implies(placed[i][j][k], square[i][j] == k + 1))

    # All numbers in the square are different.
    if n_cells > 1:
        solver.add(c5.Distinct(cells))

    # The cells hold 1 to n^2 together, so they add up to n^2 * (n^2 + 1) / 2.
    solver.add(c5.Sum(cells) == n_cells * (n_cells + 1) // 2)

    # Every row adds up to the magic sum.
    solver.add(*[c5.Sum(row) == magic_sum for row in square])

    # Every column adds up to the magic sum.
    solver.add(*[c5.Sum([square[i][j] for i in range(n)]) == magic_sum for j in range(n)])

    # The main diagonal and the other diagonal each add up to the magic sum.
    solver.add(c5.Sum([square[i][i] for i in range(n)]) == magic_sum,
          c5.Sum([square[i][n - 1 - i] for i in range(n)]) == magic_sum)

    return solver, {"square": square}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
