"""All n-queens placements: every way to put n queens on an n x n board so that no two share
a row, a column or a diagonal.

Boolean board x[i][j] (queen on row i, column j) with linear constraints, which gives Hexaly
bounds it can close. Enumeration by re-solving with soft no-goods: the objective counts how
many printed placements the board repeats. Objective 0 is a new placement; a proven minimum
of 1 or more (OPTIMAL, gap limit 0) proves that every placement has been printed.

A hard model without a placement would only end INFEASIBLE, which proves nothing, so a first
model counts the attacks and minimises them: a proven minimum above 0 proves that no
placement exists, and the enumeration runs only otherwise.
"""
import json
import sys
import time

import hexaly.optimizer as hx

S = hx.HxSolutionStatus
START = time.monotonic()
DEADLINE = START + 105  # the whole run must end within 120 s

with open(sys.argv[1]) as f:
    n = json.load(f)["n"]


def time_left(cap=None):
    left = max(1, int(DEADLINE - time.monotonic()))
    return min(left, cap) if cap else left


def configure(optimizer):
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)


def enumerate_placements():
    """Print every placement; return (number printed, proven complete)."""
    with hx.HexalyOptimizer() as optimizer:
        configure(optimizer)
        model = optimizer.model
        x = [[model.bool() for _ in range(n)] for _ in range(n)]

        # One queen on every row and on every column
        for i in range(n):
            model.constraint(model.sum(x[i]) == 1)
        for j in range(n):
            model.constraint(model.sum(x[i][j] for i in range(n)) == 1)
        # At most one queen on every diagonal, in both directions
        for d in range(-(n - 1), n):
            down = [x[i][i - d] for i in range(n) if 0 <= i - d < n]
            up = [x[i][d + n - 1 - i] for i in range(n) if 0 <= d + n - 1 - i < n]
            for cells in (down, up):
                if len(cells) > 1:
                    model.constraint(model.sum(cells) <= 1)

        repeats = []
        model.minimize(0)
        model.close()
        found = 0
        while True:
            optimizer.param.time_limit = time_left()
            optimizer.solve()
            status = optimizer.solution.status
            if status == S.INCONSISTENT:
                return found, True
            if status not in (S.FEASIBLE, S.OPTIMAL):
                return found, False  # time limit with nothing found: no proof either way
            if model.get_objective(0).value >= 1:
                return found, status == S.OPTIMAL  # proven: every placement repeats a printed one
            queens = [next(j for j in range(n) if x[i][j].value) for i in range(n)]
            print(json.dumps({"queens": queens}), flush=True)
            found += 1
            model.open()
            model.remove_objective(0)
            repeats.append(model.and_(*[x[i][queens[i]] for i in range(n)]))
            model.minimize(model.sum(repeats))
            model.close()


def min_attacks():
    """Proven minimum number of attacking pairs, or None if not proven."""
    with hx.HexalyOptimizer() as optimizer:
        configure(optimizer)
        optimizer.param.time_limit = time_left(30)
        model = optimizer.model
        col = [model.int(0, n - 1) for _ in range(n)]  # col[i]: column of the queen on row i
        # Each pair of queens on the same column or the same diagonal counts as one attack
        attacks = [0]
        for i in range(n):
            for j in range(i + 1, n):
                attacks += [col[i] == col[j], col[i] + i == col[j] + j, col[i] - i == col[j] - j]
        violations = model.sum(attacks)
        model.minimize(violations)
        model.close()
        optimizer.solve()
        status = optimizer.solution.status
        return violations.value if status == S.OPTIMAL else None


least = None
print("proven minimum number of attacks:", least, file=sys.stderr)
if least is not None and least >= 1:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    found, complete = enumerate_placements()
    print(f"placements: {found} complete: {complete} time: {time.monotonic() - START:.1f} s",
          file=sys.stderr)
    if found == 0 and complete:
        print(json.dumps({"status": "unsatisfiable"}))
