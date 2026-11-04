# csplib_067_quasigroup_completion: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Complete a partially filled N-by-N table so that each of the numbers 1 to N
    occurs exactly once in every row and every column (a quasigroup, or Latin square)."""
    n = instance["N"]          # order of the quasigroup
    start = instance["start"]  # start[r][c]: the given number in cell (r, c), or 0 if the cell is empty
    rng = range(n)             # indices of the rows, the columns and the numbers

    # x[r][c][v] is true when cell (r, c) holds the number v + 1
    x = [[[Bool(f"x_{r}_{c}_{v}") for v in rng] for c in rng] for r in rng]

    constraints = []

    # Each cell holds exactly one number.
    for r in rng:
        for c in rng:
            constraints.append(sum(x[r][c]) == 1)

    # Each row holds each number exactly once.
    for r in rng:
        for v in rng:
            constraints.append(sum(x[r][c][v] for c in rng) == 1)

    # Each column holds each number exactly once.
    for c in rng:
        for v in rng:
            constraints.append(sum(x[r][c][v] for r in rng) == 1)

    # A given cell keeps its number.
    for r in rng:
        for c in rng:
            g = start[r][c]
            if g != 0:
                constraints.append(x[r][c][g - 1] == 1)

    # The completed table: the number in each cell.
    puzzle = [[sum((v + 1) * x[r][c][v] for v in rng) for c in rng] for r in rng]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"puzzle": puzzle}


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
