"""All n-queens placements: every way to put n queens on an n x n board so that no two share
a row, a column or a diagonal.

Whether any placement exists is settled first by minimising diagonal attacks. Then a Boolean
per square with linear row, column and diagonal sums; solutions are enumerated by
re-solving with soft no-goods over the n squares that hold queens; a proven minimum of 1
repeat proves that no placement is missing.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
deadline = time.monotonic() + 95  # the whole run must end within 120 s

with open(sys.argv[1]) as f:
    n = json.load(f)["n"]


def time_left():
    return max(1, int(deadline - time.monotonic()))


def diagonals(board):
    """The cells of every diagonal with at least two squares."""
    cells = [[board[r][r - d] for r in range(n) if 0 <= r - d < n] for d in range(-(n - 2), n - 1)]
    cells += [[board[r][s - r] for r in range(n) if 0 <= s - r < n] for s in range(1, 2 * n - 2)]
    return cells


def fewest_attacks():
    """Minimum number of extra queens on diagonals with one queen per row and column, or None
    if not proven. Above 0 proves that no placement exists (with hard diagonals the first
    solve would only end INFEASIBLE at its time limit, which proves nothing)."""
    with hx.HexalyOptimizer() as optimizer:
        param = optimizer.param
        param.verbosity = 0
        param.nb_threads = 4
        param.set_gap_limit(0)
        param.time_limit = 20
        model = optimizer.model
        queen = [[model.bool() for _ in range(n)] for _ in range(n)]
        for r in range(n):
            model.constraint(model.sum(queen[r]) == 1)
        for c in range(n):
            model.constraint(model.sum(queen[r][c] for r in range(n)) == 1)
        attacks = model.sum(model.max(0, model.sum(cells) - 1) for cells in diagonals(queen))
        model.minimize(attacks)
        model.close()
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            return 1
        return attacks.value if status == S.OPTIMAL else None


# Settle first whether any placement exists
attacks = fewest_attacks()
if attacks is not None and attacks > 0:
    print(f"no placement exists: at least {attacks} attack(s), proven", file=sys.stderr)
    sys.exit()

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # OPTIMAL must mean the bound is reached exactly
    model = optimizer.model
    queen = [[model.bool() for _ in range(n)] for _ in range(n)]  # queen[r][c]: a queen on (r, c)

    # One queen in every row
    for r in range(n):
        model.constraint(model.sum(queen[r]) == 1)
    # One queen in every column
    for c in range(n):
        model.constraint(model.sum(queen[r][c] for r in range(n)) == 1)
    # At most one queen on every diagonal
    for cells in diagonals(queen):
        model.constraint(model.sum(cells) <= 1)

    # Soft no-goods: the objective counts the earlier placements repeated. Each no-good is
    # the and of the n squares holding that placement's queens.
    repeats = []
    model.minimize(0)
    model.close()
    found, complete = [], False
    while True:
        param.time_limit = time_left()
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break  # time limit with nothing found: no proof either way
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL  # proven: every placement repeats a found one
            break
        columns = [next(c for c in range(n) if queen[r][c].value) for r in range(n)]
        found.append(columns)
        print(json.dumps({"queens": columns}), flush=True)
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[queen[r][columns[r]] for r in range(n)]))
        model.minimize(model.sum(repeats))
        model.close()

    print(f"solutions {len(found)} complete {complete} status {status.name}", file=sys.stderr)
