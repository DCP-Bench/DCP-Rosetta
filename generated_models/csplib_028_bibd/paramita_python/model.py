# csplib_028_bibd: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_028_bibd.py csplib_028_bibd.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object
    is in exactly r blocks, and every two distinct objects are together in exactly l blocks.
    The answer is the v by b incidence matrix."""
    v = instance["v"]    # the number of objects
    b = instance["b"]    # the number of blocks
    r = instance["r"]    # the number of blocks each object is in
    k = instance["k"]    # the number of objects in each block
    lam = instance["l"]  # the number of blocks in which every two distinct objects are together

    # matrix[i][j] is true when object i is in block j
    matrix = [[Bool(f"x_{i}_{j}") for j in range(b)] for i in range(v)]

    constraints = []

    # Each object is in exactly r blocks.
    constraints += [sum(matrix[i]) == r for i in range(v)]

    # Each block holds exactly k objects.
    constraints += [sum(matrix[i][j] for i in range(v)) == k for j in range(b)]

    # Every two distinct objects are together in exactly lam blocks.
    for i in range(v):
        for i2 in range(i + 1, v):
            # both[j] is true when objects i and i2 are both in block j
            both = []
            for j in range(b):
                p = Bool(f"both_{i}_{i2}_{j}")
                constraints.append(Iff(p, matrix[i][j] & matrix[i2][j]))
                both.append(p)
            constraints.append(sum(both) == lam)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"matrix": matrix}


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
