# kenken: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install ortools`):
#   python kenken.py kenken.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row and column holds each
    digit once, and the digits of each cage achieve the cage's target with its operation."""
    n = instance["n"]            # the grid is n by n, with digits 1..n
    cages = instance["problem"]  # the cages: each has its target and the cells it covers

    model = cp_model.CpModel()

    # x[r][c] is the digit in the cell at row r, column c.
    x = [[model.new_int_var(1, n, f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    def way(condition):
        """A flag that is true only when the condition holds."""
        flag = model.new_bool_var("way")
        model.add(condition).only_enforce_if(flag)
        return flag

    # Each row holds each digit exactly once.
    for r in range(n):
        model.add_all_different(x[r])

    # Each column holds each digit exactly once.
    for c in range(n):
        model.add_all_different([x[r][c] for r in range(n)])

    # Each cage achieves its target. The operation is not given, so a cage may use any
    # operation that is valid for its size. Digits may repeat within a cage.
    for target, cells in cages:
        # The digits in the cells of the cage.
        cage = [x[r - 1][c - 1] for r, c in cells]
        # The product of the digits in the cage.
        product = model.new_int_var(1, n ** len(cage), "cage_product")
        model.add_multiplication_equality(product, cage)

        # ways holds a flag for each way the cage can reach its target.
        if len(cage) == 2:
            # Two cells: their sum, product, difference (either order) or exact quotient
            # (either order) equals the target.
            a, b = cage
            ways = [
                way(a + b == target),
                way(product == target),
                way(a - b == target),
                way(b - a == target),
                way(a * target == b),
                way(b * target == a),
            ]
        else:
            # Three or more cells: the sum or the product of the digits equals the target.
            ways = [way(sum(cage) == target), way(product == target)]
        model.add_bool_or(ways)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
