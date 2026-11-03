# heterosquare: a hermax (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install hermax`):
#   python heterosquare.py heterosquare.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Fill an n x n square with the distinct integers 1..n^2 so that the n row sums,
    the n column sums and the two diagonal sums are all different from one another.
    This is a satisfaction problem: any such square is an answer."""
    n = instance["n"]  # order of the square: n rows, n columns
    cells = n * n      # the entries are the distinct integers 1..cells

    m = Model()

    # x[i][j] is the entry in row i, column j (0-based), a value from 1 to cells
    x = m.int_matrix("x", n, n, 1, cells)

    # Every entry is different from every other one.
    m &= m.vector([x[i][j] for i in range(n) for j in range(n)]).all_different()

    # The 2n + 2 lines of the square: the n rows, the n columns and the two diagonals.
    lines = ([[x[i][j] for j in range(n)] for i in range(n)]               # row i
             + [[x[j][i] for j in range(n)] for i in range(n)]             # column i
             + [[x[i][i] for i in range(n)],                               # main diagonal
                [x[i][n - 1 - i] for i in range(n)]])                      # anti-diagonal

    # A sum of n distinct values from 1..cells lies between 1+2+...+n and
    # (cells) + (cells-1) + ... + (cells-n+1). These bounds come from the problem,
    # not from the instance's data beyond n.
    lowest_sum = n * (n + 1) // 2
    highest_sum = n * cells - n * (n - 1) // 2

    # line_sum[k] is the sum of line k (rows first, then columns, then the two diagonals)
    line_sum = []
    for k, line in enumerate(lines):
        s = m.int(f"line_sum_{k}", lowest_sum, highest_sum)
        m &= (s == sum_expr(line))
        line_sum.append(s)

    # The n row sums, n column sums and two diagonal sums are all different.
    m &= m.vector(line_sum).all_different()

    # Implied: the n row sums together add up to all the entries, 1 + 2 + ... + cells.
    # This helps the solver; it does not change which squares are answers.
    m &= (sum_expr(line_sum[:n]) == cells * (cells + 1) // 2)

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
