# session1_money_change: a Paramita (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python session1_money_change.py session1_money_change.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Alice gives Bob change using the coins she has available: compose the
    amount from the available coins, minimizing the number of coins used."""
    amount = instance["amount"]              # the change Alice gives Bob
    types = instance["types_of_coins"]       # types[k]: the value of coin type k
    available = instance["available_coins"]  # available[k]: how many coins of type k Alice has
    n_types = len(types)                     # the number of coin types

    # given[k][j] is true when Alice gives Bob at least j+1 coins of type k
    given = [[Bool(f"coin_{k}_ge_{j + 1}") for j in range(available[k])] for k in range(n_types)]

    subject_to = []  # the rules the change must satisfy

    # Giving at least j+2 coins of a type means giving at least j+1 of them.
    for k in range(n_types):
        for j in range(available[k] - 1):
            subject_to.append(If(given[k][j + 1], given[k][j]))

    # The coins given add up to the amount.
    subject_to.append(sum(types[k] * b for k in range(n_types) for b in given[k]) == amount)

    # coin_counts[k] is the number of coins of type k given to Bob
    coin_counts = [sum(given[k]) for k in range(n_types)]

    # The number of coins given, which Alice keeps as small as possible.
    total_coins = sum(coin_counts)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_coins, And(subject_to), to_cnf, formula, pool)

    return (formula, pool), {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
