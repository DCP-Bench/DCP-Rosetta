# fancy_dress: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python fancy_dress.py

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    # t is true when he wears a green tie, which costs $10
    t = Bool("t")
    # h is true when he wears a green hat, which costs $2
    h = Bool("h")
    # r is true when he wears the green shirt he already owns, which costs nothing
    r = Bool("r")
    # s is true when he wears green socks, which cost $12
    s = Bool("s")
    # n is true when he pays the $11 entrance fee
    n = Bool("n")

    # Rule 1: a green tie requires a green shirt.
    rule1 = If(t, r)

    # Rule 2: green socks and a green shirt together require a green tie or a green hat.
    rule2 = If(s & r, t | h)

    # Rule 3: a green shirt, a green hat, or no green socks requires a green tie.
    rule3 = If(r | h | ~s, t)

    # Rule 4: he pays the fee exactly when he breaks one of rules 1 to 3.
    constraints = [Iff(n, ~(rule1 & rule2 & rule3))]

    # total is what he pays: the tie, the hat, the socks and the fee.
    total = 10 * t + 2 * h + 12 * s + 11 * n

    outputs = {"t": t, "h": h, "r": r, "s": s, "n": n}

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(constraints), to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    (formula, pool), outputs = create_model({})

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
