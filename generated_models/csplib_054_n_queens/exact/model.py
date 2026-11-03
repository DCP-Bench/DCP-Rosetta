# csplib_054_n_queens: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from exact import Exact


def pick_value(solver, name, lo, hi):
    """Return one 0/1 variable per value from lo to hi, with exactly one of them 1: the
    one for the value that the variable name takes."""
    flags = {v: f"{name}_is_{v}" for v in range(lo, hi + 1)}
    for flag in flags.values():
        solver.addVariable(flag, 0, 1)
    solver.addConstraint([(1, f) for f in flags.values()], True, 1, True, 1)
    solver.addConstraint([(v, flags[v]) for v in flags] + [(-1, name)], True, 0, True, 0)
    return flags


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n_queens = instance["n"]  # the board size, which is also the number of queens

    solver = Exact()

    # Exact identifies its variables by name.
    # queens[i] is the column, from 1 to n, of the queen in row i
    queens = [f"q{i}" for i in range(n_queens)]
    for name in queens:
        solver.addVariable(name, 1, n_queens)
    # in_column[name][v] is 1 when the queen named name is in column v
    in_column = {name: pick_value(solver, name, 1, n_queens) for name in queens}

    # No two queens share a column.
    for value in range(1, n_queens + 1):
        solver.addConstraint([(1, in_column[name][value]) for name in queens], False, 0, True, 1)

    # No two queens share a diagonal: queens in rows i and j are on one when their
    # columns differ by the same amount as their rows.
    for i in range(n_queens):
        for j in range(i + 1, n_queens):
            for v in range(1, n_queens + 1):
                for w in (v + (j - i), v - (j - i)):
                    if 1 <= w <= n_queens:
                        solver.addConstraint([(1, in_column[queens[i]][v]), (1, in_column[queens[j]][w])],
                                             False, 0, True, 1)

    return solver, {"queens": queens}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
