# kakuro: a PuLP (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python kakuro.py kakuro.json

import pulp


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell of an n by n grid so that the digits
    of each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the black cells, which hold no digit
    entries = instance["problem"]  # the entries: each one a clue and the white cells it covers

    # the black cells, by grid position
    black = {(row - 1, col - 1) for row, col in blanks}

    # x[r][c] is the digit in the cell at row r, column c; a black cell holds 0
    x = [[0 if (r, c) in black else pulp.LpVariable(f"x_{r}_{c}", 0, 9, cat="Integer")
          for c in range(n)] for r in range(n)]

    # the white cells: those that belong to an entry
    white = sorted({(r - 1, c - 1) for entry in entries for r, c in entry[1:]})

    # holds[(r, c)][d - 1] is 1 when the white cell (r, c) holds the digit d, else 0
    holds = {}
    problem = pulp.LpProblem("kakuro", pulp.LpMinimize)
    for r, c in white:
        holds[(r, c)] = [pulp.LpVariable(f"holds_{r}_{c}_{d}", cat="Binary") for d in range(1, 10)]
        # each white cell holds exactly one digit, and that digit is its value in x
        problem += pulp.lpSum(holds[(r, c)]) == 1
        problem += x[r][c] == pulp.lpSum(d * holds[(r, c)][d - 1] for d in range(1, 10))

    for entry in entries:
        clue, cells = entry[0], [(r - 1, c - 1) for r, c in entry[1:]]
        # the digits of the entry add up to its clue
        problem += pulp.lpSum(x[r][c] for r, c in cells) == clue
        # no digit appears twice in the entry
        for d in range(9):
            problem += pulp.lpSum(holds[cell][d] for cell in cells) <= 1

    return problem, {"x": x}


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
