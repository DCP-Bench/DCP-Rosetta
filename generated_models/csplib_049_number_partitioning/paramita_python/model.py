# csplib_049_number_partitioning: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Split the numbers 1 to n into two sets A and B of equal size, with equal sums and equal
    sums of squares."""
    n = instance["n"]        # the numbers 1 to n are split between A and B
    numbers = range(1, n + 1)
    half = n // 2            # the size of each set

    # a[i][j] is true when number i is the j-th number of A
    a = {i: [Bool(f"a_{i}_{j}") for j in range(half)] for i in numbers}
    # b[i][j] is true when number i is the j-th number of B
    b = {i: [Bool(f"b_{i}_{j}") for j in range(half)] for i in numbers}

    # Each number is in exactly one of A and B.
    constraints = [sum(a[i]) + sum(b[i]) == 1 for i in numbers]

    # Each position in A and in B holds one number, so A and B both have half of the numbers.
    for j in range(half):
        constraints.append(sum(a[i][j] for i in numbers) == 1)
        constraints.append(sum(b[i][j] for i in numbers) == 1)

    # A and B have the same sum.
    constraints.append(sum(i * a[i][j] for i in numbers for j in range(half))
                       == sum(i * b[i][j] for i in numbers for j in range(half)))

    # A and B have the same sum of squares.
    constraints.append(sum(i * i * a[i][j] for i in numbers for j in range(half))
                       == sum(i * i * b[i][j] for i in numbers for j in range(half)))

    # slot_a[j] is the number at position j of A, and slot_b[j] the one of B.
    slot_a = [sum(i * a[i][j] for i in numbers) for j in range(half)]
    slot_b = [sum(i * b[i][j] for i in numbers) for j in range(half)]

    # The numbers of A are in increasing order, and so are those of B.
    for j in range(half - 1):
        constraints.append(slot_a[j] + 1 <= slot_a[j + 1])
        constraints.append(slot_b[j] + 1 <= slot_b[j + 1])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"A": slot_a, "B": slot_b}


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
