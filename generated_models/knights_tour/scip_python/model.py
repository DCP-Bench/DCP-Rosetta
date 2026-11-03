# knights_tour: a SCIP (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python knights_tour.py knights_tour.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A knight moves on an n x n chessboard and must visit every square exactly once,
    each move going to a square a knight's move away from the previous one. The tour
    need not return to its starting square. Output x[r][c] is the move number
    (0 to n*n-1) at which the knight stands on row r, column c."""
    n = instance["n"]  # the side of the chessboard: it has n x n squares
    N = n * n          # the number of squares, which is also the number of move numbers, 0 to N-1

    # Squares are numbered s = r * n + c for row r and column c. A knight's move
    # changes the row and the column by 1 and 2 in some order, so two squares are
    # a knight's move apart when their absolute row and column differences multiply to 2.
    row, col = np.divmod(np.arange(N), n)
    adjacent = (np.abs(row[:, None] - row[None, :]) * np.abs(col[:, None] - col[None, :]) == 2).astype(int)

    model = Model("knights_tour")

    # step[s, t] is 1 when the knight moves directly from square s to square t. Only
    # knight's-move pairs can be steps: ub=adjacent fixes the other pairs to 0. This
    # gives at most 8 N step variables, where a variable per square and move number
    # would give N * N.
    step = model.addMatrixVar((N, N), vtype="B", ub=adjacent, name="step")
    # start[s] is 1 when the tour starts on square s, and end[s] when it ends there.
    start = model.addMatrixVar(N, vtype="B", name="start")
    end = model.addMatrixVar(N, vtype="B", name="end")

    # Every square is entered by exactly one step, except the starting square, which
    # is entered by none. Every square is left by exactly one step, except the end.
    model.addMatrixCons(step.sum(axis=0) + start == 1)
    model.addMatrixCons(step.sum(axis=1) + end == 1)
    # The tour starts on exactly one square.
    model.addCons(start.sum() == 1)

    # move[s] is the move number of square s, from 0 at the start to N-1 at the end.
    # Bounds 0 and N-1 come from the N squares of the tour (the first and last move).
    move = model.addMatrixVar(N, vtype="I", lb=0, ub=N - 1, name="move")
    # The steps form one path from the start to the end, plus possibly some cycles.
    # The move numbers below rule out cycles, so the path goes through every square.
    # No all-different is needed: the move numbers grow along the path, so its N
    # squares get N different values from 0 to N-1.
    for s, t in zip(*np.nonzero(adjacent)):
        # addMatrixCons takes no indicator, so each knight's-move pair gets one:
        # if the step from s to t is made, then t is at least one move after s.
        model.addConsIndicator(move[t] - move[s] >= 1, binvar=step[s, t])

    # SCIP branches first on the variables with the higher priority. The steps get 1000,
    # the move numbers the default 0: the search then follows the path step by step.
    # Branching on the move numbers first wanders, and a second tour can take minutes.
    for variable in step.flatten():
        model.chgVarBranchPriority(variable, 1000)

    # The problem asks for any tour, so the model has no objective.
    return model, {"x": move.reshape(n, n)}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
