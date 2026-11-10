# calvin_puzzle: a Paramita (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python calvin_puzzle.py calvin_puzzle.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]            # the grid has n rows and n columns
    n_squares = n * n            # one square for each number from 1 to n^2
    numbers = range(n_squares)   # the number k + 1 is written as k, from 0

    # p[r][c][k] is true when square (r, c) holds the number k + 1
    p = [[[Bool(f"p_{r}_{c}_{k}") for k in numbers] for c in range(n)] for r in range(n)]

    constraints = []  # the rules of the puzzle

    # Every square holds exactly one number.
    for r in range(n):
        for c in range(n):
            constraints.append(sum(p[r][c]) == 1)

    # Every number is written in exactly one square.
    for k in numbers:
        constraints.append(sum(p[r][c][k] for r in range(n) for c in range(n)) == 1)

    # The steps the next number can take: three squares along a row or column, or two
    # squares along a diagonal, as (row change, column change).
    moves = [(0, 3), (0, -3), (3, 0), (-3, 0),
             (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # If square (r, c) holds k + 1, the number k + 2 is one step away from it. A square
    # with no square one step away cannot hold k + 1.
    for k in numbers[:-1]:
        for r in range(n):
            for c in range(n):
                next_squares = [p[r + dr][c + dc][k + 1]
                                for dr, dc in moves
                                if 0 <= r + dr < n and 0 <= c + dc < n]
                if next_squares:
                    constraints.append(~p[r][c][k] | Or(next_squares))
                else:
                    constraints.append(~p[r][c][k])

    # x[r][c] is the number in square (r, c)
    x = [[sum((k + 1) * p[r][c][k] for k in numbers) for c in range(n)] for r in range(n)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
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
