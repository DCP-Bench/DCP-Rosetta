# csplib_076_costas_arrays: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Place n marks on an n-by-n grid, one per row and one per column, so that the
    n(n-1)/2 vectors between the marks are all different (a Costas array)."""
    n = instance["n"]       # size of the grid and number of marks
    vals = range(1, n + 1)  # the columns, numbered 1 to n
    pos = range(n)          # the rows, numbered 0 to n-1
    constraints = []

    # xv[i][v] is true when the mark in row i is in column v
    xv = [{v: Bool(f"x_{i}_{v}") for v in vals} for i in pos]

    # Each row has exactly one mark.
    for i in pos:
        constraints.append(sum(xv[i].values()) == 1)

    # Each column has exactly one mark.
    for v in vals:
        constraints.append(sum(xv[i][v] for i in pos) == 1)

    # Every possible difference between two columns.
    diffs = range(-(n - 1), n)

    # Difference triangle: line gap holds the column difference of every two marks
    # that are gap rows apart. No difference occurs twice in one line.
    for gap in range(1, n):
        pairs = []
        for i in range(n - gap):
            j = i + gap
            # diff[d] is true when the mark in row i is d columns to the left of the mark in row j
            diff = {d: Bool(f"diff_{gap}_{i}_{d + n}") for d in diffs}
            for u in vals:
                for w in vals:
                    constraints.append(If(xv[i][u] & xv[j][w], diff[u - w]))
            constraints.append(sum(diff.values()) == 1)
            pairs.append(diff)
        for d in diffs:
            constraints.append(sum(pair[d] for pair in pairs) <= 1)

    # The column of the mark in each row, numbered 1 to n.
    costas = [sum(v * xv[i][v] for v in vals) for i in pos]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"costas": costas}


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
