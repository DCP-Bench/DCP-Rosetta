# hidato: a PuLP (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python hidato.py hidato.json

import pulp


def create_model(instance):
    """A hidato puzzle is a grid partly filled with numbers. Fill the empty cells with the
    numbers 1 to rows * columns, each once, so that every number is next to the next one,
    horizontally, vertically or diagonally."""
    puzzle = instance["puzzle"]  # puzzle[r][c] is the number printed in row r, column c, 0 when empty
    rows, cols = len(puzzle), len(puzzle[0])
    n_cells = rows * cols  # the numbers are 1 to n_cells

    # The cells of the grid, and each given cell with its number.
    squares = [(r, c) for r in range(rows) for c in range(cols)]
    givens = [((r, c), puzzle[r][c]) for r, c in squares if puzzle[r][c] > 0]

    # A satisfaction problem: any filling that follows the rules will do.
    problem = pulp.LpProblem("hidato", pulp.LpMinimize)

    # The number of moves from cell p to cell q, when a move goes to any touching cell.
    def apart(p, q):
        return max(abs(p[0] - q[0]), abs(p[1] - q[1]))

    # Cell p can hold the number k only if p is the given cell holding k. An empty cell
    # can hold k only if it is within reach of every given number g: consecutive numbers
    # touch, so the cell is at most |k - g| moves from the cell of g.
    def possible(p, k):
        if puzzle[p[0]][p[1]] > 0:
            return k == puzzle[p[0]][p[1]]
        return all(apart(p, q) <= abs(k - g) for q, g in givens)

    # put[(p, k)] is 1 when cell p holds the number k, for each placement the rules allow.
    put = {(p, k): pulp.LpVariable(f"put_{p[0]}_{p[1]}_{k}", cat="Binary")
           for p in squares for k in range(1, n_cells + 1) if possible(p, k)}
    # x[r][c] is the number in row r, column c.
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n_cells, cat="Integer") for c in range(cols)]
         for r in range(rows)]

    # Each cell holds exactly one number, and x is that number.
    for p in squares:
        options = [k for k in range(1, n_cells + 1) if (p, k) in put]
        problem += pulp.lpSum(put[(p, k)] for k in options) == 1
        problem += x[p[0]][p[1]] == pulp.lpSum(k * put[(p, k)] for k in options)

    # Each number from 1 to n_cells is in exactly one cell.
    for k in range(1, n_cells + 1):
        problem += pulp.lpSum(put[(p, k)] for p in squares if (p, k) in put) == 1

    # The given numbers stay in their cells.
    for p, g in givens:
        problem += put[(p, g)] == 1

    # The cells touching cell (r, c), horizontally, vertically or diagonally: up to eight.
    def neighbours(r, c):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    # Consecutive numbers touch. If cell p holds k, one cell next to p holds k + 1, and
    # one cell next to p holds k - 1.
    for (p, k), var in put.items():
        near = neighbours(*p)
        if k < n_cells:
            problem += var <= pulp.lpSum(put[(q, k + 1)] for q in near if (q, k + 1) in put)
        if k > 1:
            problem += var <= pulp.lpSum(put[(q, k - 1)] for q in near if (q, k - 1) in put)

    return problem, {"x": x}


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
