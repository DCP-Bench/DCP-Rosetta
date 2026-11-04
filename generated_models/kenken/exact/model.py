# kenken: an Exact (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python kenken.py kenken.json

from itertools import product

from exact import Exact


def reaches_target(values, result):
    """Whether the digits of a cage reach its target. A two-cell cage reaches it by sum,
    product, difference or quotient, in either order. A larger cage, or a single cell,
    reaches it by sum or product."""
    if len(values) == 2:
        a, b = values
        return (a + b == result or a * b == result or a * result == b
                or b * result == a or a - b == result or b - a == result)
    product_of_values = 1
    for value in values:
        product_of_values *= value
    return sum(values) == result or product_of_values == result


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and every column holds each
    digit once, and the digits of each cage achieve the cage's target with one operation.
    Digits may repeat within a cage."""
    n = instance["n"]  # side of the grid, and the largest digit
    cages = instance["problem"]  # cages[k]: the target of cage k and the cells it covers, counted from 1
    digits = range(1, n + 1)

    solver = Exact()

    # Exact identifies its variables by name.
    # holds[i][j][v-1] is 1 when cell (i, j) holds digit v, and 0 when not
    holds = [[[f"cell_{i}_{j}_holds_{v}" for v in digits] for j in range(n)] for i in range(n)]
    # x[i][j] is the digit in cell (i, j)
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, n)
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # each cell holds exactly one digit
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
            # x is the digit the cell holds
            solver.addConstraint([(v, holds[i][j][v - 1]) for v in digits] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    for v in digits:
        for k in range(n):
            # each row has the digit v exactly once
            solver.addConstraint([(1, holds[k][j][v - 1]) for j in range(n)], True, 1, True, 1)
            # each column has the digit v exactly once
            solver.addConstraint([(1, holds[i][k][v - 1]) for i in range(n)], True, 1, True, 1)

    # Each cage is a choice of one digit combination that reaches its target. combo[t] is 1
    # when the cage takes its t-th combination, and the cells of the cage hold the digits of
    # the chosen combination.
    for c, (result, segment) in enumerate(cages):
        cells = [(r - 1, col - 1) for r, col in segment]  # the grid positions of the cage's cells
        combinations = [values for values in product(digits, repeat=len(cells))
                        if reaches_target(values, result)]
        if not combinations:
            # no digits reach this cage's target, so the puzzle has no solution
            solver.addVariable(f"cage_{c}_unreachable", 0, 0)
            solver.addConstraint([(1, f"cage_{c}_unreachable")], True, 1)
            continue
        combo = [f"cage_{c}_combination_{t}" for t in range(len(combinations))]
        for name in combo:
            solver.addVariable(name, 0, 1)
        # the cage takes exactly one combination
        solver.addConstraint([(1, name) for name in combo], True, 1, True, 1)
        # a cell of the cage holds the digit that the chosen combination gives its place
        for place, (i, j) in enumerate(cells):
            for v in digits:
                supporting = [(1, combo[t]) for t, values in enumerate(combinations) if values[place] == v]
                solver.addConstraint(supporting + [(-1, holds[i][j][v - 1])], True, 0, True, 0)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
