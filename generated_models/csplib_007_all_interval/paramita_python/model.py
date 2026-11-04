# csplib_007_all_interval: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Arrange the pitch classes 0 to n - 1, each once, in a series whose neighbouring
    intervals are exactly the distances 1 to n - 1, each once."""
    n = instance["n"]  # the number of pitch classes, and of notes in the series

    # x[i][v] is true when the note at position i has pitch class v
    x = [[Bool(f"x_{i}_{v}") for v in range(n)] for i in range(n)]
    # d[k][t] is true when the notes at positions k and k + 1 are t + 1 apart
    d = [[Bool(f"d_{k}_{t}") for t in range(n - 1)] for k in range(n - 1)]

    constraints = []

    # Each position holds exactly one pitch class.
    constraints += [sum(x[i]) == 1 for i in range(n)]
    # Each pitch class is used at exactly one position.
    constraints += [sum(x[i][v] for i in range(n)) == 1 for v in range(n)]

    # Each pair of neighbouring notes has exactly one interval.
    constraints += [sum(d[k]) == 1 for k in range(n - 1)]
    # The interval between neighbours at positions k and k + 1 is the distance between
    # their pitch classes.
    for k in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    constraints.append(If(x[k][a] & x[k + 1][b], d[k][abs(a - b) - 1]))

    # Each interval from 1 to n - 1 occurs between exactly one pair of neighbours.
    constraints += [sum(d[k][t] for k in range(n - 1)) == 1 for t in range(n - 1)]

    # The pitch class at each position.
    pitch = [sum(v * x[i][v] for v in range(n)) for i in range(n)]
    # The interval between each pair of neighbours.
    diffs = [sum((t + 1) * d[k][t] for t in range(n - 1)) for k in range(n - 1)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": pitch, "diffs": diffs}


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
