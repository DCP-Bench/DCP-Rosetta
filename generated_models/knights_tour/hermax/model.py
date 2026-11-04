# knights_tour: a hermax (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install hermax`):
#   python knights_tour.py knights_tour.json

from hermax.model import Model

# The eight moves of a knight, as (row change, column change). These belong to the rules of chess.
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def create_model(instance):
    """Number the squares of an n x n chessboard 0..n*n-1 so that a knight, starting on
    the square numbered 0, visits the squares in numerical order, each move a knight's
    move. The tour does not have to return to its start."""
    n = instance["n"]  # the board is n x n squares
    squares = n * n    # the number of squares; the move numbers run 0..n*n-1

    m = Model()

    # x[i][j] is the move number at which the knight stands on the square in row i, column j (the declared output)
    x = m.int_matrix("x", n, n, 0, squares - 1)

    # Every square has a different move number. There are n*n squares and n*n numbers,
    # so the numbers are exactly 0..n*n-1: the knight visits each square once.
    m &= x.flatten().all_different()

    cells = [(i, j) for i in range(n) for j in range(n)]  # every square of the board as (row, column)

    def reach(cell):
        # the squares a knight can move to from a cell, in one move, on this board
        i, j = cell
        return [(i + di, j + dj) for di, dj in KNIGHT_MOVES if 0 <= i + di < n and 0 <= j + dj < n]

    # step[(a, b)] is true when the knight's tour goes straight from square a to square b
    step = {}
    for a in cells:
        for b in reach(a):
            step[(a, b)] = m.bool(f"step_{a[0]}_{a[1]}_to_{b[0]}_{b[1]}")
            # Tour: when the knight steps from a to b, b's move number is one more than a's.
            m &= (x[b[0]][b[1]] - x[a[0]][a[1]] == 1).only_if(step[(a, b)])

    # Each square is left by exactly one step, except the last square of the tour.
    # The matching rule that each square is entered by exactly one step, except the first,
    # is implied (all_different plus the out-steps already fix every step as k -> k+1).
    # It is kept because it helps propagation: without it the search did not finish
    # within the 180 s evaluator timeout.
    for a in cells:
        out_steps = [step[(a, b)] for b in reach(a)]
        in_steps = [step[(b, a)] for b in reach(a)]
        m &= (sum(out_steps) + (x[a[0]][a[1]] == squares - 1) == 1)
        m &= (sum(in_steps) + (x[a[0]][a[1]] == 0) == 1)

    # Nothing is optimised: any knight's tour is an answer.
    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
