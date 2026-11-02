"""N-queens: place n queens on an n by n board so that no two share a row, a column or a diagonal.

Solved as a violation model: one queen per row and per column are hard constraints, and the
objective counts how far each diagonal exceeds one queen. A proven minimum of 0 is a placement;
a proven minimum above 0 proves that no placement exists.
Prints {"queens": [...]} or {"status": "unsatisfiable"}.
"""
import json
import sys

import hexaly.optimizer as hx

S = hx.HxSolutionStatus

with open(sys.argv[1]) as f:
    n = json.load(f)["n"]

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)  # a proven minimum must be exact
    optimizer.param.time_limit = 90
    model = optimizer.model
    queen = [[model.bool() for _ in range(n)] for _ in range(n)]  # queen[r][c]: a queen on row r, column c

    # No two queens share a row: exactly one queen per row
    for r in range(n):
        model.constraint(model.sum(queen[r]) == 1)
    # No two queens share a column: exactly one queen per column
    for c in range(n):
        model.constraint(model.sum(queen[r][c] for r in range(n)) == 1)

    # No two queens share a diagonal: each diagonal's excess over one queen is a violation
    diagonals = [[queen[r][c] for r in range(n) for c in range(n) if r - c == d] for d in range(-(n - 1), n)]
    diagonals += [[queen[r][c] for r in range(n) for c in range(n) if r + c == s] for s in range(2 * n - 1)]
    excess = [model.max(0, model.sum(cells) - 1) for cells in diagonals if len(cells) >= 2]
    attacks = model.sum(excess)
    model.minimize(attacks)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    value = attacks.value if status in (S.OPTIMAL, S.FEASIBLE) else None
    print(f"status {status.name} violations {value}", file=sys.stderr)
    if status == S.INCONSISTENT or (status == S.OPTIMAL and value >= 1):
        print(json.dumps({"status": "unsatisfiable"}))
    elif status in (S.OPTIMAL, S.FEASIBLE) and value == 0:
        print(json.dumps({"queens": [next(c for c in range(n) if queen[r][c].value) for r in range(n)]}))
    else:
        print("undecided within the time limit", file=sys.stderr)
        sys.exit(1)
