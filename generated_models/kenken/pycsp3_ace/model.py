# kenken: a PyCSP3 model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python kenken.py kenken.json

from pycsp3 import *


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that each row and each column holds
    every digit once, and each cage's digits give its result under one of its operations:
    a one-cell cage holds its result, a two-cell cage adds, subtracts, multiplies or divides
    (exactly) to it, and a larger cage adds or multiplies to it."""
    n = instance["n"]              # the grid has n rows and n columns
    problem = instance["problem"]  # problem[k] is [result, cells] of cage k; cells are 1-based [row, column]

    # x[r][c] is the digit in row r and column c (0-based)
    x = VarArray(size=[n, n], dom=range(1, n + 1), id="x")

    # each cage as its result and its 0-based cells
    cages = [(result, [(r - 1, c - 1) for r, c in cells]) for result, cells in problem]

    # the auxiliary products that stand in for a product of four or more cells; ACE 2.6
    # accepts invalid tuples for a Product over four or more variables
    partial_products = []
    # the rule each cage's digits must satisfy
    cage_rules = []
    for index, (result, cells) in enumerate(cages):
        # the digits of the cage's cells
        cage = [x[r][c] for r, c in cells]
        if len(cage) == 1:
            cage_rules.append(cage[0] == result)
        elif len(cage) == 2:
            # two cells may use any of the four operations; a division must be exact
            cage_rules.append(Or(
                cage[0] + cage[1] == result,
                abs(cage[0] - cage[1]) == result,
                cage[0] * cage[1] == result,
                cage[0] == result * cage[1],
                cage[1] == result * cage[0],
            ))
        elif len(cage) == 3:
            # a three-cell cage adds or multiplies to its result
            cage_rules.append(Or(Sum(cage) == result, Product(cage) == result))
        else:
            # partial[j] is the product of the first j + 2 cells, and each partial is at most
            # n ** (j + 2) <= n ** len(cage), the largest product of the cage's digits
            partial = VarArray(size=len(cage) - 1, dom=range(1, n ** len(cage) + 1), id=f"partial{index}")
            partial_products.append(partial[0] == cage[0] * cage[1])
            partial_products.extend(partial[j] == partial[j - 1] * cage[j + 1] for j in range(1, len(partial)))
            # a larger cage adds or multiplies to its result
            cage_rules.append(Or(Sum(cage) == result, partial[-1] == result))

    satisfy(
        # each row holds each digit once
        [AllDifferent(row) for row in x],
        # each column holds each digit once
        [AllDifferent(column) for column in columns(x)],
        # the partial products of the cages
        partial_products,
        # the digits of each cage give its result
        cage_rules,
    )

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
