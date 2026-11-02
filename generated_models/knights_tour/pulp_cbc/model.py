# knights_tour: a PuLP (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python knights_tour.py knights_tour.json

import pulp


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without returning
    to its starting square. The squares are numbered by move, from 0 to n * n - 1."""
    n = instance["n"]  # the board is n by n
    cells = n * n      # the number of squares; the moves are numbered 0 to cells - 1
    squares = [(r, c) for r in range(n) for c in range(n)]

    problem = pulp.LpProblem("knights_tour", pulp.LpMinimize)

    # the knight's moves, as (change in row, change in column)
    jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    # the squares a knight can jump to from square (r, c)
    def reachable(r, c):
        return [(r + dr, c + dc) for dr, dc in jumps if 0 <= r + dr < n and 0 <= c + dc < n]

    # x[r][c] is the move number of the square in row r, column c
    x = [[pulp.LpVariable(f"x_{r}_{c}", 0, cells - 1, cat="Integer") for c in range(n)]
         for r in range(n)]

    # jump[(p, q)] is 1 when the knight jumps straight from square p to square q
    jump = {(p, q): pulp.LpVariable(f"jump_{p[0]}_{p[1]}_{q[0]}_{q[1]}", cat="Binary")
            for p in squares for q in reachable(*p)}

    # first[p] is 1 for the square the tour starts on, and last[p] is 1 for the square it ends on
    first = {p: pulp.LpVariable(f"first_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    last = {p: pulp.LpVariable(f"last_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    problem += pulp.lpSum(first.values()) == 1
    problem += pulp.lpSum(last.values()) == 1

    for p in squares:
        r, c = p
        # Every square except the start is entered by one jump, and every square except the
        # end is left by one jump.
        problem += pulp.lpSum(jump[(q, p)] for q in reachable(r, c)) == 1 - first[p]
        problem += pulp.lpSum(jump[(p, q)] for q in reachable(r, c)) == 1 - last[p]
        # The start has move number 0 and the other squares have move numbers from 1. The end
        # has move number cells - 1 and the other squares have move numbers up to cells - 2.
        problem += x[r][c] <= (cells - 1) * (1 - first[p])
        problem += x[r][c] >= 1 - first[p]
        problem += x[r][c] >= (cells - 1) * last[p]
        problem += x[r][c] <= cells - 2 + last[p]

    # A jump from p to q takes the knight from move k to move k + 1. Without that jump, the
    # two move numbers may differ by any amount up to cells - 1. Following the jumps from
    # the start gives move numbers that rise by one at every jump, so the jumps cannot close
    # into a loop, and the squares are numbered 0, 1, 2, ... without gaps.
    for (p, q), j in jump.items():
        problem += x[q[0]][q[1]] >= x[p[0]][p[1]] + 1 - cells * (1 - j)
        problem += x[q[0]][q[1]] <= x[p[0]][p[1]] + 1 + (cells - 2) * (1 - j)

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
