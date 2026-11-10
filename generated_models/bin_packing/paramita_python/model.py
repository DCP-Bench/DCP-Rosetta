# bin_packing: a Paramita (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python bin_packing.py bin_packing.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Assign each item to one of the bins so that the total weight of the items in each bin
    does not exceed the bin capacity."""
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight a bin can hold
    n_bins = instance["num_bins"]    # the number of bins
    n_items = len(weights)           # the number of items

    # in_bin[i][b] is true when item i goes into bin b
    in_bin = [[Bool(f"in_bin_{i}_{b}") for b in range(n_bins)] for i in range(n_items)]
    # bins[i] is the bin of item i, numbered from 0
    bins = [sum(b * in_bin[i][b] for b in range(n_bins)) for i in range(n_items)]

    constraints = []

    # Each item goes into exactly one bin.
    for i in range(n_items):
        constraints.append(sum(in_bin[i]) == 1)

    # The items in each bin weigh no more than the capacity.
    for b in range(n_bins):
        constraints.append(sum(weights[i] * in_bin[i][b] for i in range(n_items)) <= capacity)

    # The bins are interchangeable, so item i is put in one of the first i + 1 bins.
    for i in range(n_items):
        for b in range(i + 1, n_bins):
            constraints.append(~in_bin[i][b])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"bins": bins}


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
