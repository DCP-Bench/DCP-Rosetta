# birthday_coins: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python birthday_coins.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to one pound,
    five shillings and six pence. How many half-crowns was he given?"""
    shilling = 12                                 # pence in a shilling
    sixpence = 6                                  # pence in a sixpence
    half_crown = 2 * shilling + sixpence          # pence in a half-crown: two shillings and sixpence
    total = (20 + 5) * shilling + sixpence        # one pound, five shillings and six pence, in pence
    n_coins = 15                                  # the number of coins Tommy was given

    # count_flags(kind)[v] is true when Tommy has v coins of that kind; he has at least one of each kind
    def count_flags(kind):
        return {v: Bool(f"{kind}_is_{v}") for v in range(1, n_coins + 1)}

    # The number of coins of a kind, from its count flags.
    def count_of(flags):
        return sum(v * flag for v, flag in flags.items())

    half_crown_flags = count_flags("half_crowns")
    shilling_flags = count_flags("shillings")
    sixpence_flags = count_flags("sixpences")
    n_half_crowns = count_of(half_crown_flags)
    n_shillings = count_of(shilling_flags)
    n_sixpences = count_of(sixpence_flags)

    cons = []   # all constraints of the puzzle

    # Each kind of coin has exactly one count.
    for flags in (half_crown_flags, shilling_flags, sixpence_flags):
        cons.append(sum(flags.values()) == 1)

    # The three counts add up to the coins given.
    cons.append(n_half_crowns + n_shillings + n_sixpences == n_coins)
    # The coins are worth one pound, five shillings and six pence.
    cons.append(half_crown * n_half_crowns + shilling * n_shillings + sixpence * n_sixpences == total)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"half_crowns": n_half_crowns}


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
