"""All n-queens solutions: every placement of n queens on an n by n board with no two sharing
a row, a column or a diagonal.

A Boolean per square with linear row, column and diagonal sums (rows posted before columns).
Feasibility is settled first by minimising the diagonal attacks: a proven minimum above 0
means there is no placement to list. Then the placements are enumerated by re-solving with
soft no-goods: the objective counts how many earlier placements the board repeats; a proven
minimum of 1 or more means none is left.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
START = time.monotonic()
BUDGET = 90  # seconds for the whole program


def time_left():
    return max(1, int(BUDGET - (time.monotonic() - START)))


def diagonals(n):
    """The squares of every diagonal holding at least two squares."""
    lines = []
    for d in range(-(n - 1), n):  # r - c == d
        lines.append([(r, r - d) for r in range(n) if 0 <= r - d < n])
    for s in range(2 * n - 1):  # r + c == s
        lines.append([(r, s - r) for r in range(n) if 0 <= s - r < n])
    return [line for line in lines if len(line) > 1]


def board(model, n):
    q = [[model.bool() for _ in range(n)] for _ in range(n)]  # q[r][c]: a queen on row r, column c
    # Every row holds exactly one queen
    for r in range(n):
        model.constraint(model.sum(q[r]) == 1)
    # Every column holds exactly one queen
    for c in range(n):
        model.constraint(model.sum(q[r][c] for r in range(n)) == 1)
    return q


def configure(optimizer):
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = time_left()


with open(sys.argv[1]) as f:
    n = json.load(f)["n"]

if n <= 1:  # one placement (n = 1) or the empty placement (n = 0), nothing to search
    print(json.dumps({"queens": [0] * n}))
    sys.exit(0)

# Settle feasibility: minimise the number of extra queens on the diagonals
with hx.HexalyOptimizer() as optimizer:
    configure(optimizer)
    model = optimizer.model
    q = board(model, n)
    excess = []
    for line in diagonals(n):
        e = model.int(0, len(line) - 1)
        model.constraint(model.sum(q[r][c] for r, c in line) <= 1 + e)
        excess.append(e)
    violations = model.sum(excess)
    model.minimize(violations)
    model.close()
    optimizer.solve()
    status = optimizer.solution.status
    if status == S.INCONSISTENT or (status == S.OPTIMAL and violations.value >= 1):
        print("no placement exists (proven)", file=sys.stderr)
        sys.exit(0)
    if not (status == S.OPTIMAL and violations.value == 0):
        print("feasibility not settled:", status.name, file=sys.stderr)
        sys.exit(1)

# Enumerate every placement with soft no-goods
with hx.HexalyOptimizer() as optimizer:
    configure(optimizer)
    model = optimizer.model
    q = board(model, n)
    # No two queens share a diagonal
    for line in diagonals(n):
        model.constraint(model.sum(q[r][c] for r, c in line) <= 1)

    repeats = []
    model.minimize(0)
    model.close()
    count, complete = 0, False
    while True:
        optimizer.param.time_limit = time_left()
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
        queens = [next(c for c in range(n) if q[r][c].value) for r in range(n)]
        count += 1
        print(json.dumps({"queens": queens}), flush=True)
        model.open()
        model.remove_objective(0)
        # The board repeats this placement when every one of its queen squares holds a queen
        # (with one queen per row this fixes the whole board; 8-queens proved faster this way
        # than with an equality on every square)
        repeats.append(model.and_(*[q[r][queens[r]] for r in range(n)]))
        model.minimize(model.sum(repeats))
        model.close()

    print("solutions:", count, "complete:", complete,
          "seconds: %.2f" % (time.monotonic() - START), file=sys.stderr)
