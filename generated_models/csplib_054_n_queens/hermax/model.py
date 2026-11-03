# csplib_054_n_queens: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from hermax.model import Model


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens attack each other,
    that is, no two share a row, a column, or a diagonal. Each row holds exactly one
    queen, and queens[i] says in which column (1 to n) the queen of row i stands."""
    n = instance["n"]  # n: the board is n x n, and n queens are placed on it

    m = Model()

    # queens[i] is the column (1..n) of the queen in row i
    queens = m.int_vector("queens", n, 1, n)

    # hermax's all_different takes variables, not expressions such as queens[i] + i, so
    # each diagonal index gets its own auxiliary IntVar, tied to the queen by the equations below.
    # up[i] = column + row of the queen in row i: constant along each diagonal running
    # down to the left (up to the right), so two queens sharing an up[] value attack each other.
    up = m.int_vector("up", n, 1, 2 * n - 1)
    # down[i] = column - row of the queen in row i: constant along each diagonal running
    # down to the right (up to the left).
    down = m.int_vector("down", n, 1 - (n - 1), n)
    for i in range(n):
        m &= (up[i] == queens[i] + i)
        m &= (down[i] == queens[i] - i)

    # The queens occupy different columns: each column holds at most one queen.
    m &= queens.all_different()
    # No two queens share an up-diagonal (the diagonal from the bottom-left to the top-right).
    m &= up.all_different()
    # No two queens share a down-diagonal (the diagonal from the top-left to the bottom-right).
    m &= down.all_different()

    # Satisfaction problem: no objective.
    return m, {"queens": queens}


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
