# kenken: a hermax (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install hermax`):
#   python kenken.py kenken.json

import itertools

from hermax.model import Model


def create_model(instance):
    """KenKen: fill an n x n grid with the digits 1..n so that every row and every column
    holds each digit exactly once, and every cage (a group of cells with a target number)
    reaches its target. Digits may repeat inside a cage. A two-cell cage reaches its target
    by a sum, a product, a difference or an exact quotient of its two digits, in either
    order; a larger cage by the sum or the product of its digits."""
    n = instance["n"]  # the grid is n x n, and its digits are 1..n
    # cages[c] = [target, cells] for the c-th cage: the cage's target number, and its
    # cells as [row, col] pairs counted from 1
    cages = instance["problem"]

    m = Model()

    # x[i][j] is the digit in row i, column j (0-based), the declared output
    x = m.int_matrix("x", n, n, 1, n)

    # Each row and each column contains every digit exactly once.
    for i in range(n):
        m &= x.row(i).all_different()
        m &= x.col(i).all_different()

    # Does this assignment of digits to the cells of a cage reach the target?
    def meets(target, digits):
        if len(digits) == 2:
            a, b = digits
            return (a + b == target or a * b == target or a * target == b
                    or b * target == a or a - b == target or b - a == target)
        product = 1
        for d in digits:
            product *= d
        return sum(digits) == target or product == target

    # Each cage's cells take a combination of digits that reaches its target. The
    # combinations are enumerated here and posted as one table over the cage's cells.
    for target, cells in cages:
        allowed = [digits for digits in itertools.product(range(1, n + 1), repeat=len(cells))
                   if meets(target, digits)]
        m &= m.table([x[row - 1][col - 1] for row, col in cells], allowed=allowed)

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
