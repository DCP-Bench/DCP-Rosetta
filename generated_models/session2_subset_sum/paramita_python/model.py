# session2_subset_sum: a Paramita (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session2_subset_sum.py session2_subset_sum.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A bank van had several kinds of bags of coins, with a fixed number of coins
    in each kind and many bags of each kind. Thieves stole some bags holding a
    given total number of coins: find how many bags of each kind were stolen."""
    coin_numbers = instance["coin_numbers"]    # coin_numbers[i]: the number of coins in a bag of kind i
    total_lost = instance["total_coins_lost"]  # the total number of coins that were lost

    # counts[i][k] is true when exactly k bags of kind i were stolen. The count
    # goes up to the most bags of kind i that could hold the lost coins.
    counts = []
    for i, coins in enumerate(coin_numbers):
        most_bags = total_lost // coins
        counts.append([Bool(f"bags_{i}_{k}") for k in range(most_bags + 1)])

    # A kind of bag has exactly one stolen count.
    subject_to = [sum(kind) == 1 for kind in counts]

    # The stolen bags hold exactly the coins that were lost.
    coins_lost = sum(coins * k * counts[i][k]
                     for i, coins in enumerate(coin_numbers)
                     for k in range(1, len(counts[i])))
    subject_to.append(coins_lost == total_lost)

    # bags[i]: the number of stolen bags of kind i
    bags = [sum(k * counts[i][k] for k in range(1, len(counts[i])))
            for i in range(len(coin_numbers))]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"bags": bags}


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
