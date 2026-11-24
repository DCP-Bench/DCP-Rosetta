# birthday_coins: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python birthday_coins.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf

N_COINS = 15  # the coins Tommy was given
VALUE = 240 + 5 * 12 + 6  # £1 5s 6d in pence: a pound is 240 pence, a shilling 12
PENCE = {"half_crowns": 30, "shillings": 12, "sixpences": 6}  # pence per coin of each kind


def create_model(instance):
    """Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence) or a
    sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
    worth £1 5s 6d. How many half-crowns could he have been given?"""
    # The instance has no fields: every number above is from the problem statement.

    # at_least[kind][k - 1] is true when he was given at least k coins of that kind
    # (k = 1..15). A kind may be absent, when none of its Bools is true.
    at_least = {kind: [Bool(f"{kind}_ge_{k}") for k in range(1, N_COINS + 1)] for kind in PENCE}

    # Having at least k + 1 coins of a kind means having at least k.
    constraints = [If(ge[k + 1], ge[k]) for ge in at_least.values() for k in range(N_COINS - 1)]

    # How many coins of each kind he was given: the number of true Bools.
    count = {kind: sum(ge) for kind, ge in at_least.items()}

    # He was given 15 coins.
    constraints.append(sum(count.values()) == N_COINS)

    # They add up to £1 5s 6d.
    constraints.append(sum(PENCE[kind] * count[kind] for kind in PENCE) == VALUE)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"half_crowns": count["half_crowns"]}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

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
