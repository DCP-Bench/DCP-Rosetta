# csplib_023_magic_hexagon: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from docplex.mp.model import Model


def create_model(instance):
    """Magic hexagon: place the numbers 1 to NUM_CELLS, each once, in the 19 cells of a hexagon
    (rows of 3, 4, 5, 4, 3) so that each of the 15 lines of cells (rows and diagonals) adds up
    to MAGIC_SUM."""
    num_cells = instance["NUM_CELLS"]  # number of cells of the hexagon, filled with 1..NUM_CELLS
    magic_sum = instance["MAGIC_SUM"]  # what every line of cells adds up to
    cells = range(num_cells)
    numbers = range(1, num_cells + 1)

    model = Model("magic_hexagon")

    # holds[c, v] is 1 when cell c holds number v. Every cell holds one number and every
    # number is used exactly once (all different).
    holds = model.binary_var_matrix(cells, numbers, name="holds")
    model.add_constraints(model.sum(holds[c, v] for v in numbers) == 1 for c in cells)
    model.add_constraints(model.sum(holds[c, v] for c in cells) == 1 for v in numbers)

    # LD[c] is the number in cell c, the cells counted row by row (A, B, ..., S).
    LD = [model.sum(v * holds[c, v] for v in numbers) for c in cells]

    # The cells are named as in the problem:
    #       A, B, C
    #      D, E, F, G
    #     H, I, J, K, L
    #      M, N, O, P
    #       Q, R, S
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s = LD

    # Each of the 15 lines of the hexagon adds up to the magic sum.
    lines = [
        # rows
        [a, b, c], [d, e, f, g], [h, i, j, k, l], [m, n, o, p], [q, r, s],
        # diagonals, top-left to bottom-right
        [a, d, h], [b, e, i, m], [c, f, j, n, q], [g, k, o, r], [l, p, s],
        # diagonals, top-right to bottom-left
        [c, g, l], [b, f, k, p], [a, e, j, o, s], [d, i, n, r], [h, m, q],
    ]
    model.add_constraints(model.sum(line) == magic_sum for line in lines)

    return model, {"LD": LD}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
