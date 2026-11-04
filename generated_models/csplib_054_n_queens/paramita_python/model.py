# csplib_054_n_queens: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Place n queens on an n by n chessboard so that no two queens share a row,
    a column or a diagonal."""
    n = instance["n"]  # the side of the board, and the number of queens

    # queen[i][c] is true when the queen in row i stands in column c
    queen = [[Bool(f"queen_{i}_{c}") for c in range(n)] for i in range(n)]

    constraints = []

    # Each row holds exactly one queen.
    constraints += [sum(queen[i]) == 1 for i in range(n)]

    # Each column holds exactly one queen.
    constraints += [sum(queen[i][c] for i in range(n)) == 1 for c in range(n)]

    # No two queens share a diagonal running down to the left (cells with the same i + c).
    for s in range(2 * n - 1):
        cells = [queen[i][c] for i in range(n) for c in range(n) if i + c == s]
        if len(cells) > 1:
            constraints.append(sum(cells) <= 1)

    # No two queens share a diagonal running down to the right (cells with the same i - c).
    for d in range(-(n - 1), n):
        cells = [queen[i][c] for i in range(n) for c in range(n) if i - c == d]
        if len(cells) > 1:
            constraints.append(sum(cells) <= 1)

    # The column, from 1 to n, of the queen in each row.
    queens = [sum((c + 1) * queen[i][c] for c in range(n)) for i in range(n)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"queens": queens}


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
