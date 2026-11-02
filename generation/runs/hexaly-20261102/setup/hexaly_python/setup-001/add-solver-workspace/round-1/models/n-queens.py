"""N-queens: place n queens on an n x n board, one per row, so that no two share a column or a diagonal.

Search alone never proves that no placement exists, so the attacks are counted and minimised:
a proven minimum of 0 is a placement, a proven minimum above 0 proves there is none.
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
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 60
    model = optimizer.model
    # col[i] is the column of the queen in row i, so no two queens share a row
    col = [model.int(0, n - 1) for _ in range(n)]

    # Each pair of queens on the same column or the same diagonal counts as one attack
    attacks = []
    for i in range(n):
        for j in range(i + 1, n):
            attacks.append(col[i] == col[j])
            attacks.append(col[i] + i == col[j] + j)
            attacks.append(col[i] - i == col[j] - j)
    violations = model.sum(attacks) if attacks else model.sum([0])
    model.minimize(violations)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    value = violations.value if status in (S.OPTIMAL, S.FEASIBLE) else None
    print("status:", status.name, "attacks:", value, file=sys.stderr)
    if value == 0:
        print(json.dumps({"queens": [c.value for c in col]}))
    elif status == S.OPTIMAL or status == S.INCONSISTENT:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print("no placement found and no proof that none exists", file=sys.stderr)
