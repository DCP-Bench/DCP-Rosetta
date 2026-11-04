# csplib_023_magic_hexagon: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import pulp


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the 19 cells of a hexagon so that each of
    the 15 straight lines of cells (rows and both diagonal directions) adds up to the magic sum."""
    num_cells = instance["NUM_CELLS"]  # the number of cells in the hexagon, 19
    magic_sum = instance["MAGIC_SUM"]  # the sum each straight line of cells has to reach

    # The cells A to S, numbered 0 to 18 in reading order from the top row.
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s = range(num_cells)
    lines = [
        # the five rows
        [a, b, c], [d, e, f, g], [h, i, j, k, l], [m, n, o, p], [q, r, s],
        # the five diagonals running from top left to bottom right
        [a, d, h], [b, e, i, m], [c, f, j, n, q], [g, k, o, r], [l, p, s],
        # the five diagonals running from top right to bottom left
        [c, g, l], [b, f, k, p], [a, e, j, o, s], [d, i, n, r], [h, m, q],
    ]
    cells = range(num_cells)
    numbers = range(1, num_cells + 1)

    problem = pulp.LpProblem("magic_hexagon", pulp.LpMinimize)

    # holds[x][v] is 1 when cell x has the number v, and 0 when not.
    holds = [[pulp.LpVariable(f"holds_{x}_{v}", cat="Binary") for v in numbers] for x in cells]
    # The number in cell x.
    LD = [pulp.lpSum(v * holds[x][v - 1] for v in numbers) for x in cells]

    # Each cell has exactly one number.
    for x in cells:
        problem += pulp.lpSum(holds[x]) == 1
    # Each number is used in exactly one cell.
    for v in numbers:
        problem += pulp.lpSum(holds[x][v - 1] for x in cells) == 1

    # Each of the 15 lines adds up to the magic sum.
    for line in lines:
        problem += pulp.lpSum(LD[x] for x in line) == magic_sum

    # Symmetry breaking. Turning the hexagon or mirroring it keeps the lines as lines, so every
    # arrangement comes with 11 equivalent copies. The six corners in clockwise order from A
    # are A, C, L, S, Q, H. Requiring A to hold the smallest corner number, and C a smaller
    # number than H, keeps one copy of each family.
    corners = [a, c, l, s, q, h]
    for corner in corners[1:]:
        problem += LD[a] + 1 <= LD[corner]
    problem += LD[c] + 1 <= LD[h]

    return problem, {"LD": LD}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
