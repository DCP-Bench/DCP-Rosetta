# coin3_application: a Paramita (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python coin3_application.py coin3_application.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Find the fewest coins that let one pay exactly any amount below a given maximum,
    using coins of the given denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable

    constraints = []  # the rules the coins carried must follow
    x = []   # x[i] is the number of coins of type i carried
    ge = []  # ge[i][k - 1] is true when at least k coins of type i are carried

    for i, d in enumerate(denominations):
        # a payment below max_amount uses at most (max_amount - 1) // d coins of value d, so no more are carried
        max_coins = (max_amount - 1) // d
        at_least = [Bool(f"x_{i}_ge_{k}") for k in range(1, max_coins + 1)]
        # at least k + 1 coins implies at least k coins
        constraints += [If(at_least[k], at_least[k - 1]) for k in range(1, max_coins)]
        ge.append(at_least)
        x.append(sum(at_least))

    # payable[v] is true when amount v can be paid with the coin types so far.
    # With no coin types, only the amount 0 can be paid.
    payable = [Bool(f"r_0_{v}") for v in range(max_amount)]
    constraints.append(payable[0])
    constraints += [~payable[v] for v in range(1, max_amount)]

    for j, d in enumerate(denominations):
        # the amount v is payable when, for some k, it is payable without this coin type
        # after taking away k coins of value d, and at least k coins of this type are carried
        new_payable = [Bool(f"r_{j + 1}_{v}") for v in range(max_amount)]
        for v in range(max_amount):
            options = []  # one option per number k of coins of this type used
            for k in range(0, v // d + 1):
                if k > len(ge[j]):
                    break
                base = payable[v - k * d]
                options.append(base if k == 0 else And(base, ge[j][k - 1]))
            constraints.append(Iff(new_payable[v], options[0] if len(options) == 1 else Or(options)))
        payable = new_payable

    # every amount from 1 to max_amount - 1 is payable with the coins carried
    constraints += [payable[a] for a in range(1, max_amount)]

    # carry as few coins as possible
    total = sum(x)  # the number of coins carried, over all coin types

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of coins, minimised (its negation
    # is what the soft clauses maximise).
    return (formula, pool), {"x": x}, total


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

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
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")
