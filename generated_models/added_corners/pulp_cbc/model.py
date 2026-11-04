# added_corners: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install pulp numpy`) with:
#   python added_corners.py

import pulp


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    # There are eight cells, and each holds one of the digits 1 to 8.
    n = 8
    problem = pulp.LpProblem("corners", pulp.LpMinimize)

    # The cells run 0 to 2 along the top, 3 and 4 at the sides of the middle row, and 5 to 7 along the bottom.
    # Cells 0, 2, 5 and 7 are circles; cells 1, 3, 4 and 6 are squares.
    # pick[i][v] is 1 when digit v is in cell i, and 0 when not.
    pick = pulp.LpVariable.dicts("pick", (range(n), range(1, n + 1)), cat="Binary")

    # position_i is the digit in cell i.
    positions = [pulp.LpVariable(f"position_{i}", 1, n, cat="Integer") for i in range(n)]

    # Each cell holds exactly one digit, and that digit is the one picked for it.
    for i in range(n):
        problem += pulp.lpSum(pick[i][v] for v in range(1, n + 1)) == 1
        problem += positions[i] == pulp.lpSum(v * pick[i][v] for v in range(1, n + 1))

    # Each digit goes in exactly one cell.
    for v in range(1, n + 1):
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    # Each square holds the sum of the two circles next to it.
    for square, first, second in ((1, 0, 2), (3, 0, 5), (4, 2, 7), (6, 5, 7)):
        problem += positions[square] == positions[first] + positions[second]

    return problem, {"positions": positions}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
