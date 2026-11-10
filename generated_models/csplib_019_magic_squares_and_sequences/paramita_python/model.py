# csplib_019_magic_squares_and_sequences: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1} between
    0 and n-1 such that, for every i, the number i occurs exactly x_i times in the
    sequence."""
    n = instance["n"]  # the length of the sequence

    # is_value[i][w] is true when entry i of the sequence is w
    is_value = [{w: Bool(f"is_value_{i}_{w}") for w in range(n)} for i in range(n)]

    constraints = []

    # Each entry takes exactly one value.
    for i in range(n):
        constraints.append(sum(is_value[i].values()) == 1)

    # The number i occurs exactly x_i times, so the entries equal to i add up to the
    # value of entry i.
    for i in range(n):
        occurrences = sum(is_value[j][i] for j in range(n))
        value = sum(w * is_value[i][w] for w in range(n))
        constraints.append(occurrences == value)

    # x[i]: the value of entry i of the sequence
    x = [sum(w * is_value[i][w] for w in range(n)) for i in range(n)]

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
