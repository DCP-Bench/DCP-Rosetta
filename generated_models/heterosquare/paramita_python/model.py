# heterosquare: a Paramita (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python heterosquare.py heterosquare.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square
    n_cells = n * n
    values = range(1, n_cells + 1)  # the numbers the square holds: 1 to n^2
    cells = [(i, j) for i in range(n) for j in range(n)]  # (row, column) of each cell

    # x[i][j][v] is true when the cell in row i and column j holds the number v.
    x = [[{v: Bool(f"x_{i}_{j}_{v}") for v in values} for j in range(n)] for i in range(n)]

    subject_to = []  # all constraints of the square

    # Every cell holds exactly one number.
    for i, j in cells:
        subject_to.append(sum(x[i][j][v] for v in values) == 1)
    # Every number from 1 to n^2 is in exactly one cell.
    for v in values:
        subject_to.append(sum(x[i][j][v] for i, j in cells) == 1)

    # square[i][j] is the number in row i and column j.
    square = [[sum(v * x[i][j][v] for v in values) for j in range(n)] for i in range(n)]

    # The lines of the square, each a list of cells: the rows, the columns and the two diagonals.
    lines = [[(i, j) for j in range(n)] for i in range(n)]
    lines += [[(i, j) for i in range(n)] for j in range(n)]
    lines.append([(k, k) for k in range(n)])
    lines.append([(k, n - 1 - k) for k in range(n)])

    # A line of n distinct numbers from 1 to n^2 sums to at least lo (the n smallest)
    # and at most hi (the n largest).
    lo = n * (n + 1) // 2
    hi = n * n_cells - n * (n - 1) // 2
    n_steps = hi - lo  # how far a line sum can rise above lo

    # at_least[a][k - 1] is true when the sum of line a is at least lo + k.
    at_least = [[Bool(f"sum_{a}_ge_{lo + k}") for k in range(1, n_steps + 1)]
                for a in range(len(lines))]

    # A line sum that reaches lo + k also reaches every smaller step.
    for flags in at_least:
        for k in range(n_steps - 1):
            subject_to.append(If(flags[k + 1], flags[k]))

    # The sum of each line is lo plus the number of steps it reaches.
    for line, flags in zip(lines, at_least):
        subject_to.append(sum(square[i][j] for i, j in line) == lo + sum(flags))

    # Any two lines have different sums: some step is reached by exactly one of them.
    for a in range(len(lines)):
        for b in range(a + 1, len(lines)):
            # differ[k] is true only when exactly one of lines a and b reaches lo + k + 1.
            differ = []
            for k in range(n_steps):
                d = Bool(f"differ_{a}_{b}_{k}")
                ua, ub = at_least[a][k], at_least[b][k]
                subject_to.append(If(d, (ua & ~ub) | (~ua & ub)))
                differ.append(d)
            subject_to.append(Or(differ))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": square}


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
