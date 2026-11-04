# csplib_015_schurs_lemma: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf


def create_model(instance):
    """Put the balls labelled 1 to n into c boxes so that no triple of balls (x, y, z)
    with x + y = z has all three balls in the same box."""
    n_balls = instance["n"]  # the number of balls, labelled 1 to n
    n_boxes = instance["c"]  # the number of boxes

    # in_box[i][j] is true when ball i is in box j
    in_box = {i: [Bool(f"in_box_{i}_{j}") for j in range(n_boxes)] for i in range(1, n_balls + 1)}

    # Each ball is in exactly one box.
    constraints = [sum(in_box[i]) == 1 for i in range(1, n_balls + 1)]

    # No triple x + y = z is in one box. Each triple is taken once, with x <= y.
    for x in range(1, n_balls + 1):
        for y in range(x, n_balls + 1):
            z = x + y
            if z > n_balls:
                break
            # The distinct balls of the triple (x = y gives two balls).
            triple = sorted({x, y, z})
            for j in range(n_boxes):
                constraints.append(Or([~in_box[b][j] for b in triple]))

    # balls[i - 1]: the box that ball i is in, numbered from 1
    balls = [sum((j + 1) * in_box[i][j] for j in range(n_boxes)) for i in range(1, n_balls + 1)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"balls": balls}


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
