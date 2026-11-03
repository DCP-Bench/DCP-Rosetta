# four_numbers: a Paramita (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python four_numbers.py four_numbers.json

from itertools import combinations

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and
    10 such that every given number is the sum of some non-empty subset of the three."""
    numbers = instance["numbers"]  # numbers[i]: the i-th number that must be a subset sum
    n_integers = 3  # how many integers to find
    values = range(1, 11)  # the values an integer to find can take

    # value_is[j][v] is true when the j-th integer to find is v.
    value_is = [{v: Bool(f"x_{j}_{v}") for v in values} for j in range(n_integers)]

    # Each integer to find is between 1 and 10 and takes exactly one value.
    subject_to = [sum(value_is[j].values()) == 1 for j in range(n_integers)]

    # x[j] is the j-th integer to find.
    x = [sum(v * value_is[j][v] for v in values) for j in range(n_integers)]

    # The non-empty subsets of the three integers.
    subsets = [S for r in (1, 2, 3) for S in combinations(range(n_integers), r)]

    for i, number in enumerate(numbers):
        # uses[S] is true when the integers in subset S add up to numbers[i].
        uses = {S: Bool(f"s_{i}_{''.join(map(str, S))}") for S in subsets}

        # Each given number is the sum of some subset.
        subject_to.append(Or(list(uses.values())))

        # The subset that is used adds up to the given number.
        for S, used in uses.items():
            subject_to.append(If(used, sum(x[j] for j in S) == number))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
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
