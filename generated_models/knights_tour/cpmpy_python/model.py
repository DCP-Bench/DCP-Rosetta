# knights_tour: a CPMpy model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python knights_tour.py knights_tour.json

import cpmpy as cp


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]  # the board is n by n
    squares = n * n

    # x[i, j] is the move at which the knight visits square (i, j), from 0 to n*n-1
    x = cp.intvar(0, squares - 1, shape=(n, n), name="x")

    # The legal knight moves, as (row step, column step): a fixed fact of chess.
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    model = cp.Model()

    # Each square is visited exactly once.
    model.add(cp.AllDifferent(x))

    # A tour that visits every square once is a Hamiltonian path. A Circuit constraint
    # states that directly and propagates better than comparing the move numbers of all
    # neighbouring squares. Circuit needs a cycle, so a dummy node (number n*n) closes the
    # path: the dummy's successor is the first square, and the last square's successor is
    # the dummy.
    # nxt[c] is the square visited right after square c = i * n + j (or the dummy if c is
    # the last square); nxt[n*n] is the first square
    nxt = cp.intvar(0, squares, shape=squares + 1, name="nxt")
    model.add(cp.Circuit(nxt))

    # From a square the knight can only go to a square a knight's move away, or end the tour.
    for i in range(n):
        for j in range(n):
            reachable = [(i + di) * n + (j + dj) for di, dj in knight_moves
                         if 0 <= i + di < n and 0 <= j + dj < n]
            model.add(cp.InDomain(nxt[i * n + j], reachable + [squares]))

    # Link the successors to the move numbers: the first square is visited at move 0, and
    # the square after c is visited one move after c. rank is the move of each square,
    # followed by the dummy node.
    rank = cp.cpm_array(list(x.flatten()) + [cp.intvar(squares, squares, name="dummy_rank")])
    model.add(rank[nxt[squares]] == 0)
    for c in range(squares):
        model.add((nxt[c] != squares).implies(rank[nxt[c]] == rank[c] + 1))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
