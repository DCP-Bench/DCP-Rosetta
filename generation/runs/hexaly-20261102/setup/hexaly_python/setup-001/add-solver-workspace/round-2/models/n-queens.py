"""N-queens: place n queens on an n by n board so that no two share a row, a column or a
diagonal.

A Boolean per square. Rows and columns are hard (one queen each, always possible); the
diagonal rule is moved into the objective as the number of extra queens on each diagonal.
A proven minimum of 0 is a solution; a proven minimum of 1 or more proves that no placement
exists (search alone with hard diagonals would only end INFEASIBLE, which proves nothing).
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    n = json.load(f)["n"]

if n <= 1:  # no diagonal holds two squares, so there is nothing to search
    print(json.dumps({"queens": [0] * n}))
    sys.exit(0)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 90
    model = optimizer.model
    q = [[model.bool() for _ in range(n)] for _ in range(n)]  # q[r][c]: a queen on row r, column c

    # Every row holds exactly one queen
    for r in range(n):
        model.constraint(model.sum(q[r]) == 1)
    # Every column holds exactly one queen
    for c in range(n):
        model.constraint(model.sum(q[r][c] for r in range(n)) == 1)

    # No two queens share a diagonal: count the queens above one on each diagonal
    excess = []
    for d in range(-(n - 1), n):  # r - c == d
        cells = [q[r][r - d] for r in range(n) if 0 <= r - d < n]
        if len(cells) > 1:
            e = model.int(0, len(cells) - 1)
            model.constraint(model.sum(cells) <= 1 + e)
            excess.append(e)
    for s in range(0, 2 * n - 1):  # r + c == s
        cells = [q[r][s - r] for r in range(n) if 0 <= s - r < n]
        if len(cells) > 1:
            e = model.int(0, len(cells) - 1)
            model.constraint(model.sum(cells) <= 1 + e)
            excess.append(e)

    violations = model.sum(excess)
    model.minimize(violations)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("status:", status.name, file=sys.stderr)
    if status == S.OPTIMAL and violations.value == 0:
        queens = [next(c for c in range(n) if q[r][c].value) for r in range(n)]
        print(json.dumps({"queens": queens}))
    elif status == S.OPTIMAL:
        # proven: every placement has at least one diagonal attack
        print("minimum attacks:", violations.value, file=sys.stderr)
        print(json.dumps({"status": "unsatisfiable"}))
    elif status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no proof either way; best violations:",
              violations.value if status == S.FEASIBLE else None, file=sys.stderr)
