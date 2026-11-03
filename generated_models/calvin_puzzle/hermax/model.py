# calvin_puzzle: a hermax (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install hermax`):
#   python calvin_puzzle.py calvin_puzzle.json

from hermax.model import Model

# The moves from one number to the next, as (row step, column step): three squares straight
# up, down, left or right, or two squares diagonally. These are the rules of the puzzle, not
# data of the instance.
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n*n, each exactly once, so that every number
    is followed by the next one a move away: three squares straight, or two squares
    diagonally. The sequence may start in any square."""
    n = instance["n"]  # side of the grid
    last = n * n  # the largest number; the numbers are 1..last

    # The squares of the grid, as (row, column) pairs.
    squares = [(i, j) for i in range(n) for j in range(n)]

    # The squares that one move from square (i, j) can reach, staying on the grid.
    def neighbours(square):
        i, j = square
        return [(i + di, j + dj) for di, dj in MOVES
                if 0 <= i + di < n and 0 <= j + dj < n]

    m = Model()
    # x[i][j] is the number written in square (i, j) (the declared output)
    x = m.int_matrix("x", n, n, 1, last)

    # Every number is written in exactly one square: the numbers are all different.
    m &= m.vector([x[i][j] for i, j in squares]).all_different()

    # step[(a, b)] is true when the number after the one in square a sits in the neighbouring
    # square b. Naming the step per pair of squares lets each one link two numbers directly.
    step = {}
    for a in squares:
        for b in neighbours(a):
            step[(a, b)] = m.bool()

    # A step from a to b means b holds the next number after the one in a: one move apart in
    # the grid, and one larger in value.
    for a in squares:
        for b in neighbours(a):
            m &= (x[b[0]][b[1]] == x[a[0]][a[1]] + 1).only_if(step[(a, b)])

    for a in squares:
        out_steps = [step[(a, b)] for b in neighbours(a)]
        in_steps = [step[(b, a)] for b in neighbours(a)]
        # Every square except the one holding the last number is followed by exactly one
        # other square, the one with the next number.
        m &= (sum(out_steps + [x[a[0]][a[1]] == last]) == 1)
        # Every square except the one holding number 1 is preceded by exactly one square,
        # the one with the number before it.
        m &= (sum(in_steps + [x[a[0]][a[1]] == 1]) == 1)

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
