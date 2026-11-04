# flow_free_game: a Paramita (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python flow_free_game.py flow_free_game.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """Flow Free: connect the two cells of each colour with a pipe, so that the pipes
    do not cross or overlap and together cover the entire board. The colour of every
    cell is the answer."""
    board = instance["board"]        # board[i][j]: the colour the puzzle gives cell (i, j), 0 if none
    n_rows = len(board)              # the number of rows
    n_cols = len(board[0])           # the number of columns
    cells = [(i, j) for i in range(n_rows) for j in range(n_cols)]  # every cell of the board
    colours = sorted({v for row in board for v in row if v > 0})   # the colours on the board
    max_level = n_rows * n_cols - 1  # the longest pipe covers every cell, so no cell is further than this from its start

    # ends[c]: the cells the puzzle gives colour c
    ends = {c: [(i, j) for (i, j) in cells if board[i][j] == c] for c in colours}

    # L[(c, p, d)] is true when cell p lies on the pipe of colour c, d steps from the start of that pipe
    L = {(c, p, d): Bool(f"lev_{c}_{p[0]}_{p[1]}_{d}")
         for c in colours for p in cells for d in range(max_level + 1)}

    # col[(c, p)] is true when cell p carries colour c
    col = {(c, p): Bool(f"col_{c}_{p[0]}_{p[1]}") for c in colours for p in cells}

    # nbrs(p): the cells directly above, below, left and right of cell p, where they lie on the board
    def nbrs(p):
        i, j = p
        out = []
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= i + di < n_rows and 0 <= j + dj < n_cols:
                out.append((i + di, j + dj))
        return out

    # the rules of the puzzle, one group at a time
    constraints = []

    # Each cell lies on exactly one pipe, at exactly one distance from that pipe's start.
    for p in cells:
        constraints.append(sum(L[(c, p, d)] for c in colours for d in range(max_level + 1)) == 1)

    # A cell carries colour c exactly when it lies on a pipe of colour c.
    for c in colours:
        for p in cells:
            constraints.append(Iff(col[(c, p)], Or([L[(c, p, d)] for d in range(max_level + 1)])))

    # Each cell the puzzle gives a colour keeps that colour.
    for c in colours:
        for p in ends[c]:
            constraints.append(col[(c, p)])

    # Each pipe starts at its first given cell, at distance 0; no other cell is at distance 0 of that colour.
    for c in colours:
        start = ends[c][0]
        constraints.append(L[(c, start, 0)])
        for p in cells:
            if p != start:
                constraints.append(~L[(c, p, 0)])

    # A cell at distance d from the start of its pipe has a neighbour on that pipe at distance d - 1.
    # So every pipe is joined to its start, with no separate loop.
    for c in colours:
        for p in cells:
            for d in range(1, max_level + 1):
                constraints.append(~L[(c, p, d)] | Or([L[(c, q, d - 1)] for q in nbrs(p)]))

    # Along a pipe, each end touches one cell of its colour and every other cell touches two.
    # So no pipe branches.
    for c in colours:
        for p in cells:
            n_same = sum(col[(c, q)] for q in nbrs(p))  # the neighbours of p that carry colour c
            if p in ends[c]:
                constraints.append(If(col[(c, p)], n_same == 1))
            else:
                constraints.append(If(col[(c, p)], n_same == 2))

    # B[i][j] is the colour of cell (i, j), as a number.
    B = [[sum(c * col[(c, (i, j))] for c in colours) for j in range(n_cols)] for i in range(n_rows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
