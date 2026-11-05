# football: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python football.py

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders and
    strikers) so that the total price is as close as possible to the GBP 30 million
    limit without going over it. Buy exactly one goalkeeper, at least two defenders,
    at least three midfielders, at least two strikers, and at least eleven players in all."""
    budget = 30000  # the most that may be spent, in GBP thousands

    # The players available in each group, with their prices in GBP thousands, so that every price is a whole number.
    goalkeepers = [("g1", 730), ("g2", 1280), ("g3", 3880)]
    defenders = [("d1", 920), ("d2", 1310), ("d3", 1620), ("d4", 2410),
                 ("d5", 2790), ("d6", 3280), ("d7", 3910), ("d8", 4570)]
    midfielders = [("m1", 1800), ("m2", 2630), ("m3", 3170), ("m4", 3769), ("m5", 4140),
                   ("m6", 4750), ("m7", 5380), ("m8", 5930), ("m9", 6780), ("m10", 7130)]
    strikers = [("s1", 4460), ("s2", 6470), ("s3", 7780), ("s4", 8390), ("s5", 9500)]

    # bought[name] is true when the player with that name is bought
    bought = {name: Bool(f"bought_{name}")
              for name, _ in goalkeepers + defenders + midfielders + strikers}

    # the rules of the squad, one group at a time
    constraints = []

    # Exactly one goalkeeper is bought.
    constraints.append(sum(bought[name] for name, _ in goalkeepers) == 1)

    # At least two defenders are bought.
    constraints.append(sum(bought[name] for name, _ in defenders) >= 2)

    # At least three midfielders are bought.
    constraints.append(sum(bought[name] for name, _ in midfielders) >= 3)

    # At least two strikers are bought.
    constraints.append(sum(bought[name] for name, _ in strikers) >= 2)

    # At least eleven players are bought in all.
    constraints.append(sum(bought.values()) >= 11)

    # Each player's bought flag, next to the player's price.
    priced = [(bought[name], price) for name, price in goalkeepers + defenders + midfielders + strikers]

    # z is the total price of the players bought, in GBP thousands.
    z = sum(price * b for b, price in priced)

    # The total price stays within the budget.
    constraints.append(z <= budget)

    # Spend as much of the budget as possible.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(z, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total price in GBP thousands, maximised
    # (the soft clauses maximise it).
    return (formula, pool), {"z": z}, z


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    (formula, pool), outputs, objective = create_model({})

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
