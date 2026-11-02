"""N-queens: place n queens on an n x n board so that no two share a row, a column or a
diagonal.

One queen per row and per column are hard constraints. The diagonals are soft: the model
minimises the number of extra queens on a diagonal. Objective 0 is a placement; a proven
minimum above 0 (OPTIMAL, gap limit 0) proves that no placement exists.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    n = json.load(f)["n"]

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # a positive minimum must be proven exactly
    param.time_limit = 90
    model = optimizer.model
    queen = [[model.bool() for _ in range(n)] for _ in range(n)]  # queen[r][c]: a queen on (r, c)

    # One queen in every row
    for r in range(n):
        model.constraint(model.sum(queen[r]) == 1)
    # One queen in every column
    for c in range(n):
        model.constraint(model.sum(queen[r][c] for r in range(n)) == 1)

    # At most one queen on every diagonal (soft: each extra queen is one violation)
    diagonals = []
    for d in range(-(n - 1), n):  # cells with r - c == d
        diagonals.append([queen[r][r - d] for r in range(n) if 0 <= r - d < n])
    for s in range(2 * n - 1):  # cells with r + c == s
        diagonals.append([queen[r][s - r] for r in range(n) if 0 <= s - r < n])
    violations = model.sum(model.max(0, model.sum(cells) - 1) for cells in diagonals if len(cells) > 1)
    model.minimize(violations)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    if status in (S.OPTIMAL, S.FEASIBLE) and violations.value == 0:
        columns = [next(c for c in range(n) if queen[r][c].value) for r in range(n)]
        print(json.dumps({"queens": columns}))
    elif status == S.INCONSISTENT or (status == S.OPTIMAL and violations.value > 0):
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print(f"undecided: {status.name}", file=sys.stderr)
    if status in (S.OPTIMAL, S.FEASIBLE):
        print(f"status {status.name} attacks {violations.value}", file=sys.stderr)
    else:
        print(f"status {status.name}", file=sys.stderr)
