# kenken: a Choco-solver (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python kenken.py kenken.json

from pychoco.model import Model


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]            # the grid is n by n, with digits 1 to n
    cages = instance["problem"]  # each cage is [target, [[row, column], ...]], cells counted from 1

    model = Model()

    # x[r][c] is the digit in the cell at row r, column c
    x = [[model.intvar(1, n, name=f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    # Each row holds each digit exactly once.
    for r in range(n):
        model.all_different(x[r]).post()

    # Each column holds each digit exactly once.
    for c in range(n):
        model.all_different([x[r][c] for r in range(n)]).post()

    # Each cage achieves its target. The operation is not given, so a cage may use any
    # operation that is valid for its size. Digits may repeat within a cage.
    for k, (target, cells) in enumerate(cages):
        # the digits in the cells of the cage
        cage = [x[r - 1][c - 1] for r, c in cells]
        if len(cage) == 2:
            # Two cells: their sum, difference (either order), product, or quotient
            # (either order) is the target.
            a, b = cage
            model.or_([
                model.arithm(a, "+", b, "=", target),
                model.arithm(a, "-", b, "=", target),
                model.arithm(b, "-", a, "=", target),
                model.times(a, b, target),
                model.times(a, target, b),
                model.times(b, target, a),
            ]).post()
        else:
            # Three or more cells: the sum or the product of the digits is the target.
            # product is the product of the digits multiplied in so far.
            product = cage[0]
            for step, cell in enumerate(cage[1:]):
                bigger = model.intvar(1, n ** (step + 2), name=f"cage_{k}_product_{step}")
                model.times(product, cell, bigger).post()
                product = bigger
            model.or_([model.sum(cage, "=", target), model.arithm(product, "=", target)]).post()

    return model, {"x": x}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
