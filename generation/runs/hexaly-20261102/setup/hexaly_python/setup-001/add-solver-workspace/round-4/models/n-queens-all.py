"""All n-queens solutions: every placement of n queens on an n by n board so that no two share
a row, a column or a diagonal.

First one solve of the violation model (diagonal excess minimised) settles whether any
placement exists. Then the placements are enumerated on a Boolean board with linear row,
column and diagonal sums, re-solving with soft no-goods; a proven minimum of 1 repeated
placement means none is missing.
Prints each placement as {"queens": [...]} on its own line.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
DEADLINE = time.monotonic() + 95


def time_left():
    return int(DEADLINE - time.monotonic())


def diagonals(board, n):
    """Every diagonal and anti-diagonal of at least two squares, as a list of squares."""
    lines = [[board[r][c] for r in range(n) for c in range(n) if r - c == d] for d in range(-(n - 1), n)]
    lines += [[board[r][c] for r in range(n) for c in range(n) if r + c == s] for s in range(2 * n - 1)]
    return [cells for cells in lines if len(cells) >= 2]


def board_model(model, n):
    queen = [[model.bool() for _ in range(n)] for _ in range(n)]  # queen[r][c]: a queen on row r, column c
    # No two queens share a row: exactly one queen per row (all rows first, then all columns)
    for r in range(n):
        model.constraint(model.sum(queen[r]) == 1)
    # No two queens share a column: exactly one queen per column
    for c in range(n):
        model.constraint(model.sum(queen[r][c] for r in range(n)) == 1)
    return queen


with open(sys.argv[1]) as f:
    n = json.load(f)["n"]

# Does any placement exist? Minimise the diagonal attacks; a proven minimum above 0 says no.
with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = max(1, time_left())
    model = optimizer.model
    queen = board_model(model, n)
    attacks = model.sum(model.max(0, model.sum(cells) - 1) for cells in diagonals(queen, n))
    model.minimize(attacks)
    model.close()
    optimizer.solve()
    status = optimizer.solution.status
    if status == S.INCONSISTENT or (status == S.OPTIMAL and attacks.value >= 1):
        print(f"proven: no placement exists ({status.name})", file=sys.stderr)
        sys.exit(0)
    if status not in (S.OPTIMAL, S.FEASIBLE) or attacks.value != 0:
        print(f"undecided within the time limit ({status.name})", file=sys.stderr)
        sys.exit(1)

# Enumerate every placement
with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4  # the bounding that proves the last step runs beside the local search
    param.set_gap_limit(0)  # OPTIMAL must mean the bound is reached exactly
    model = optimizer.model
    queen = board_model(model, n)
    # No two queens share a diagonal
    for cells in diagonals(queen, n):
        model.constraint(model.sum(cells) <= 1)

    # Soft no-goods: the objective counts the earlier placements repeated. Every placement has
    # exactly n queens, so the queens' squares alone identify it.
    repeats = []
    model.minimize(0)
    model.close()
    found, complete = 0, False
    while True:
        left = time_left()
        if left < 1:
            break
        param.time_limit = left
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break  # time limit with nothing found: no proof either way
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL  # proven: every remaining placement repeats a found one
            break
        cols = [next(c for c in range(n) if queen[r][c].value) for r in range(n)]
        print(json.dumps({"queens": cols}), flush=True)
        found += 1
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[queen[r][cols[r]] for r in range(n)]))
        model.minimize(model.sum(repeats))
        model.close()

    print(f"solutions {found} complete {complete}", file=sys.stderr)
