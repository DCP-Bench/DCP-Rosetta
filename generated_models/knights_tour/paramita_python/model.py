# knights_tour: a Paramita (Python) model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python knights_tour.py knights_tour.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """A knight visits every square of an n by n chessboard exactly once, without
    returning to the starting square. The tour numbers the squares by move, from 0."""
    n = instance["n"]       # the board is n by n
    moves = n * n           # the number of squares, which is also the number of moves
    squares = range(moves)  # square s is in row s // n and column s % n

    # at[k][s] is true when the knight stands on square s at move k
    at = [[Bool(f"v_{k}_{s}") for s in squares] for k in range(moves)]

    # The eight knight moves, as (row step, column step).
    deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

    # neighbours[s] lists the squares a knight can reach from square s in one move.
    neighbours = {}
    for s in squares:
        i, j = divmod(s, n)
        neighbours[s] = [
            (i + di) * n + (j + dj)
            for di, dj in deltas
            if 0 <= i + di < n and 0 <= j + dj < n
        ]

    cons = []  # the rules of the tour

    # The knight stands on exactly one square at each move.
    cons += [sum(at[k]) == 1 for k in range(moves)]

    # The knight visits every square exactly once.
    cons += [sum(at[k][s] for k in range(moves)) == 1 for s in squares]

    # From the square at move k, the knight moves to a square a knight can reach from it.
    for k in range(moves - 1):
        for s in squares:
            cons.append(If(at[k][s], Or([at[k + 1][t] for t in neighbours[s]])))

    # The same move read backwards: the square at move k + 1 is reached from a square at move k.
    for k in range(moves - 1):
        for t in squares:
            cons.append(If(at[k + 1][t], Or([at[k][s] for s in neighbours[t]])))

    # x[i][j] is the move at which the knight is on square (i, j).
    x = [[sum(k * at[k][i * n + j] for k in range(moves)) for j in range(n)] for i in range(n)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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
