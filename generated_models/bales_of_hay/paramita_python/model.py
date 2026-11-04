# bales_of_hay: a Paramita (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python bales_of_hay.py bales_of_hay.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """Bales of hay were weighed in all possible pairs, and the pair weights were
    written down in numerical order without saying which pair gave which weight.
    Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the pair weights, in numerical order

    top = max(weights)  # no bale weighs more than the heaviest pair it is in
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]  # the pairs of distinct bales

    # x[i][v] is true when bale i weighs v
    x = [[Bool(f"bale_{i}_{v}") for v in range(top + 1)] for i in range(n)]
    # b[i] is the weight of bale i; weight 0 adds nothing to the sum
    b = [sum(v * x[i][v] for v in range(1, top + 1)) for i in range(n)]

    constraints = []

    # Each bale has exactly one weight.
    for i in range(n):
        constraints.append(sum(x[i]) == 1)

    # The bales are listed in ascending order of weight.
    for i in range(n - 1):
        constraints.append(b[i] <= b[i + 1])

    # y[(i, j, k)] is true when the pair of bales i and j is the k-th pair weight
    y = {(i, j, k): Bool(f"pair_{i}_{j}_weight_{k}")
         for (i, j) in pairs for k in range(len(weights))}

    # The two bales of a pair weigh together the pair weight it is matched to.
    for (i, j) in pairs:
        for k, w in enumerate(weights):
            same_sum = [x[i][a] & x[j][w - a] for a in range(top + 1) if 0 <= w - a <= top]
            constraints.append(Iff(y[(i, j, k)], Or(same_sum)))

    # Each pair of bales is matched to exactly one pair weight.
    for (i, j) in pairs:
        constraints.append(sum(y[(i, j, k)] for k in range(len(weights))) == 1)

    # Each pair weight is matched to exactly one pair of bales.
    for k in range(len(weights)):
        constraints.append(sum(y[(i, j, k)] for (i, j) in pairs) == 1)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"bales": b}


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
